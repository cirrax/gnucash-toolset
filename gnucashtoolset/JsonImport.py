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
import json
import logging

import datetime
from gnucash.gnucash_business import  Invoice as gcInvoice
from gnucash.gnucash_business import  Entry   as gcEntry
from gnucash import Session, Account, Transaction, Split, GncNumeric

import Query

DENOM_QUANTITY=1000
DENOM_PRICE=1000000
DENOM_AMOUNT=1000
# Gnucash encoding:
GC_ENC='utf-8'

def json_input(obj, date_format='%Y-%m-%dT%H:%M:%S'):
    if isinstance(obj, list):
        l=[]
        for element in obj:
            l.append(json_input(element,date_format=date_format))
        return l

    if isinstance(obj, dict):
        d={}
        for key in obj:
            d[key] = json_input(obj[key],date_format=date_format)
        return d

    try:
        return datetime.datetime.strptime(obj, date_format)
    except (TypeError, ValueError):
        pass

    return obj


class JsonImport():
    def __init__(self, file, date_format):
        infile = open(file, 'r')

        with infile:
            try:
                self.src = json.load(infile, object_hook=lambda x: json_input(obj=x, date_format=date_format))
            except ValueError:
                raise SystemExit(sys.exc_info()[1])

    def post(self,book):
        for element in self.src:
            for item in element.keys():
                 getattr(self, '_' + item)(book, element[item])

    def _transfer(self,book,d):
        from_ac=book.get_root_account().lookup_by_code(d['TransferFromAC'].encode(GC_ENC))
        if not from_ac:
            raise LookupError('TransferFromAC ({0}) not found'.format(d['TransferFromAC'].encode(GC_ENC)))


        to_ac=book.get_root_account().lookup_by_code(d['TransferToAC'].encode(GC_ENC))
        if not to_ac:
            raise LookupError('TransferToAC ({0}) not found'.format(d['TransferToAC'].encode(GC_ENC)))

        if d.has_key('Currency'):
            currency=book.get_table().lookup('CURRENCY', d['Currency'].encode(GC_ENC))
        else:
            currency=book.get_table().lookup('CURRENCY', 'CHF')

        if not currency:
            raise LookupError('Currency ({0}) not found'.format(d['Currency'].encode(GC_ENC)))

        trans = Transaction(book)
        trans.BeginEdit()
        trans.SetCurrency(currency)
        date=d.get('Date',datetime.date.today())
        trans.SetDate(date.day, date.month, date.year)
        trans.SetDescription(d.get('Description', 'Auto Generated by Json import').encode(GC_ENC))

        self._initialize_split( book, d.get('Amount',0), from_ac, trans)
        self._initialize_split( book, -1*d.get('Amount',0), to_ac, trans)
        trans.CommitEdit()
        logging.info('New Transfer: Amount {0} , from:{1},  to:{2}, memo: {3}'.format(d.get('Amount',0),d['TransferFromAC'],
                     d['TransferToAC'],d.get('Description','Auto Generated by Json import').encode(GC_ENC)))




    def _payment(self,book,d):
        account=book.get_root_account().lookup_by_code(d['TransferAC'].encode(GC_ENC))
        if not account:
            raise LookupError('TransferAC not found')

        if d.has_key('BillID'):
            invoice=book.InvoiceLookupByID(d['BillID'].encode(GC_ENC))

        if not invoice:
             logging.error('Invoice {0} not found'.format(d.get('BillID','unknown').encode(GC_ENC)))

        else:
             if not invoice.IsPosted():
                 logging.warn('Invoice {0} is not yet posted'.format(d.get('BillID','unknown')))

             if invoice.IsPaid():
                 logging.warn('Invoice {0} is already paid, create credit note'.format(d.get('BillID','unknown')))

             invoice.ApplyPayment( None,  account,
                               GncNumeric(num=d.get('Amount',0)*DENOM_AMOUNT, denom=DENOM_AMOUNT), GncNumeric(1),
                               d.get('Date',datetime.date.today()),
                               d.get('Memo','File Import').decode(GC_ENC), d['BillID'].decode(GC_ENC))

             logging.info('Payment of {0} for bill {1} entered (Memo: {2})'.format(d.get('Amount',0), d['BillID'], d.get('Memo','File Import')))

         
    def _invoice(self,book, d):
         
        if d.has_key('Currency'):
            currency=book.get_table().lookup('CURRENCY', d['Currency'].decode(GC_ENC))
        else:
            currency=book.get_table().lookup('CURRENCY', 'CHF')

        if not currency:
            raise LookupError('Currency not found')

        if d.has_key('JobID'):
            for j in Query.getJobs(book):
                if j.GetID() == d['JobID'].encode(GC_ENC):
                    owner=j
                    customer=j.GetOwner()

            try:
                customer
            except NameError:
                raise LookupError('JobID ({0}) not found'.format(d['JobID']))

        else:
            owner=book.CustomerLookupByID(d['CustomerID'].decode(GC_ENC))
            customer=owner
         
        if not owner:
            raise LookupError('Customer not found')

        if not d.has_key('ID'):
            d['ID'] = book.InvoiceNextID(owner).encode(GC_ENC)

        self.obj = gcInvoice(book=book, id=d['ID'].encode(GC_ENC), currency=currency, owner=owner)

        logging.info('New Invoice {} customer: {} ({})'.format(d['ID'], customer.GetID(), customer.GetName()	))

        self.obj.SetTerms(customer.GetTerms())

        self.obj.SetNotes(d.get('Notes',self.obj.GetNotes().decode(GC_ENC)).encode(GC_ENC))

        taxtable=customer.GetTaxTable()
        for ent in d['entries']:
            entry=gcEntry(book=book,invoice=self.obj)

            entry.SetDateEntered(ent.get('DateEntered',datetime.date.today()))
            entry.SetAction(ent.get('Action',entry.GetAction().decode(GC_ENC)).encode(GC_ENC))
            entry.SetNotes(ent.get('Notes',entry.GetNotes().decode(GC_ENC)).encode(GC_ENC))
            entry.SetDescription(ent.get('Description',entry.GetDescription().decode(GC_ENC)).encode(GC_ENC))
            entry.SetQuantity(GncNumeric(num=ent.get('Quantity',0)*DENOM_QUANTITY,denom=DENOM_QUANTITY))

            entry.SetInvPrice(GncNumeric(num=ent.get('Price',0)*DENOM_PRICE,denom=DENOM_PRICE))
           
            if ent.has_key('TaxName'):
                try: book.TaxTableLookupByName(ent['TaxName'].encode(GC_ENC))
                except: raise LookupError('TaxName not found')
                entry.SetInvTaxTable(book.TaxTableLookupByName(ent['TaxName'].encode(GC_ENC)))
            else:
                entry.SetInvTaxTable(taxtable)

            entry.SetInvTaxIncluded(ent.get('TaxIncluded',entry.GetInvTaxIncluded()))
            if not book.get_root_account().lookup_by_code(ent.get('IncomeAC').encode(GC_ENC)):
                raise LookupError('IncomeAC not found')
            entry.SetInvAccount(book.get_root_account().lookup_by_code(ent.get('IncomeAC').encode(GC_ENC)))
            
        ar=book.get_root_account().lookup_by_code(str(d['AReceivableAC']))
        if not ar:
            raise LookupError('AReceivableAC not found')
        # post invoice
        self.obj.PostToAccount(ar,datetime.date.today(), datetime.date.today(),ent.get('PostMsg',''),  False, False)

        logging.info('Invoice {} posted to {}'.format(d['ID'], d['AReceivableAC']))
        
    def _initialize_split(self, book, amount, account, trans):
        split = Split(book)
        split.SetValue(GncNumeric(num=amount*DENOM_QUANTITY,denom=DENOM_QUANTITY))
        split.SetAccount(account)
        split.SetParent(trans)
        return split

