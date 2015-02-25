#
#    Copyright (C) 2014  Cirrax GmbH  http://www.cirrax.com
#    Benedikt Trefzer <benedikt.trefzer@cirrax.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#   

import sys
import json as json
import logging

import datetime
from gnucash.gnucash_business import  Invoice as gcInvoice
from gnucash.gnucash_business import  Entry   as gcEntry
from gnucash import Session, Account, Transaction, Split, GncNumeric

import Query

DATE_FORMAT='%Y-%m-%d'
DENOM_QUANTITY=1000
DENOM_PRICE=1000
DENOM_AMOUNT=1000

def json_input(obj):
    if isinstance(obj, list):
        l=[]
        for element in obj:
            l.append(json_input(element))
        return l

    if isinstance(obj, dict):
        d={}
        for key in obj:
            d[key] = json_input(obj[key])
        return d

    if isinstance(obj, unicode):
        return obj.encode('utf-8')

    return obj


class JsonImport():
    def __init__(self, file):
        infile = open(file, 'r')

        with infile:
            try:
                self.src = json.load(infile, object_hook=json_input)
            except ValueError:
                raise SystemExit(sys.exc_info()[1])

    def post(self,book):
         for element in self.src:
             for item in element.keys():
                 getattr(self, '_' + item)(book, element[item])

    def _transfer(self,book,d):
         from_ac=book.get_root_account().lookup_by_code(d['TransferFromAC'])
         try: from_ac
         except: raise LookupError('TransferFromAC not found')


         to_ac=book.get_root_account().lookup_by_code(d['TransferToAC'])
         try: to_ac
         except: raise LookupError('TransferToAC not found')

         if d.has_key('Currency'):
             currency=book.get_table().lookup('CURRENCY', d['Currency'])
         else:
             currency=book.get_table().lookup('CURRENCY', 'CHF')

         try: currency
         except: raise LookupError('Currency not found')

         trans = Transaction(book)
         trans.BeginEdit()
         trans.SetCurrency(currency)
         date=datetime.datetime.strptime(d.get('Date',datetime.date.today().strftime(DATE_FORMAT)),DATE_FORMAT)
         trans.SetDate(date.day, date.month, date.year)
         trans.SetDescription(d.get('Description','Auto Generated by Json import'))


         self._initialize_split( book, d.get('Amount',0), from_ac, trans)
         self._initialize_split( book, -1*d.get('Amount',0), to_ac, trans)
         trans.CommitEdit()
         logging.info('New Transfer: Amount {} , from:{},  to:{}, memo: {}'.format(d.get('Amount',0),d['TransferFromAC'],
                        d['TransferToAC'],d.get('Description','Auto Generated by Json import')	))




    def _payment(self,book,d):
         if d.has_key('BillID'):
            invoice=book.InvoiceLookupByID(d['BillID'])

         if  not invoice:
             raise LookupError('Invoice not found for payment')

         if not invoice.IsPosted():
              raise LookupError('Invoice is not yet posted')

         if invoice.IsPaid():
              raise LookupError('Invoice is already paid')

         account=book.get_root_account().lookup_by_code(d['TransferAC'])
         try: account
         except: raise LookupError('TransferAC not found')

         invoice.ApplyPayment( None,  account, 
                               GncNumeric(num=d.get('Amount',0)*DENOM_AMOUNT, denom=DENOM_AMOUNT), GncNumeric(1),
                               datetime.datetime.strptime(d.get('Date',datetime.date.today().strftime(DATE_FORMAT)),DATE_FORMAT),
                               d.get('Memo','File Import'), d['BillID'])

         logging.info('Payment of {} for bill {} entered (Memo: {})'.format(d.get('Amount',0), d['BillID'], d.get('Memo','File Import')))

         
    def _invoice(self,book, d):
         
         if d.has_key('Currency'):
             currency=book.get_table().lookup('CURRENCY', d['Currency'])
         else:
             currency=book.get_table().lookup('CURRENCY', 'CHF')

         try: currency
         except: raise LookupError('Currency not found')

         if d.has_key('JobID'):
             for j in Query.getJobs(book):            
                if j.GetID() == d['JobID']:
                   owner=j
                   customer=j.GetOwner()

             try: owner
             except: raise LookupError('JobID not found')

         else:
             owner=book.CustomerLookupByID(d['CustomerID'])
             customer=owner
         
         try: owner
         except: raise LookupError('Customer not found')

         if not d.has_key('ID'):
            d['ID'] = book.InvoiceNextID(owner)

         self.obj = gcInvoice(book=book, id=d['ID'], currency=currency, owner=owner)

         logging.info('New Invoice {} customer: {} ({})'.format(d['ID'], customer.GetID(), customer.GetName()	))

         self.obj.SetTerms(customer.GetTerms())

         self.obj.SetNotes(d.get('Notes',self.obj.GetNotes()))

         taxtable=customer.GetTaxTable()
         for ent in d['entries']: 
            entry=gcEntry(book=book,invoice=self.obj)

            entry.SetDateEntered(datetime.date.today())

            entry.SetAction(ent.get('Action',entry.GetAction()))
            entry.SetNotes(ent.get('Notes',entry.GetNotes()))
            entry.SetDescription(ent.get('Description',entry.GetDescription()))
            entry.SetQuantity(GncNumeric(num=ent.get('Quantity',0)*DENOM_QUANTITY,denom=DENOM_QUANTITY))

            entry.SetInvPrice(GncNumeric(num=ent.get('Price',0)*DENOM_PRICE,denom=DENOM_PRICE))
           
            if ent.has_key('TaxName'):
                try: book.TaxTableLookupByName(ent['TaxName'])
                except: raise LookupError('TaxName not found')
                entry.SetInvTaxTable(book.TaxTableLookupByName(ent['TaxName']))
            else:
                entry.SetInvTaxTable(taxtable)

            entry.SetInvTaxIncluded(ent.get('TaxIncluded',entry.GetInvTaxIncluded()))
            try: book.get_root_account().lookup_by_code(ent.get('IncomeAC'))
            except: raise LookupError('IncomeAC not found')
            entry.SetInvAccount(book.get_root_account().lookup_by_code(ent.get('IncomeAC')))
            
         ar=book.get_root_account().lookup_by_code(d['AReceivableAC'])
         try: ar
         except: raise LookupError('AReceivableAC not found')
         # post invoice 
         self.obj.PostToAccount(ar,datetime.date.today(), datetime.date.today(),ent.get('PostMsg',''),  False, False)

         logging.info('Invoice {} posted to {}'.format(d['ID'], d['AReceivableAC']))
        
    def _initialize_split(self, book, amount, account, trans):
        split = Split(book)
        split.SetValue(GncNumeric(num=amount*DENOM_QUANTITY,denom=DENOM_QUANTITY))
        split.SetAccount(account)
        split.SetParent(trans)
        return split

