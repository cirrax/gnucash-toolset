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

import datetime
from gnucash.gnucash_business import  Invoice as gcInvoice
from gnucash.gnucash_business import  Entry   as gcEntry

import Query
from gnucash import GncNumeric
import json
import JsonImport

DENOM_QUANTITY=1000
DENOM_PRICE=1000
GC_ENC='utf-8'

def fromjson_filter(x, date_format):
    try:
        return json.loads(x,object_hook= lambda y: JsonImport.json_input(obj=y,date_format=date_format))
    except ValueError:
        return x

def date_filter(x, y):
    try:
        return x.strftime(y)
    except AttributeError:
        return x

def _sorting_index(lindex, x):
    try:
        return lindex.index(x)
    except ValueError:
        for i, elem in enumerate(lindex):
            print i
            print elem
            if elem in x:
                return i

    return len(lindex) + 1

def isorting_filter(value, lindex, attr):
    return sorted(value, key=lambda x: _sorting_index(lindex,x[attr]) )

class BaseAccounting():
    def __init__(self, obj=None):
        self.obj=obj

class Invoice(BaseAccounting):

    def to_dict(self):
        assign_customer = {
            'Customer' : lambda x: x,
            'Job'      : lambda x: x.GetOwner(),
        }
	if self.obj==None:
	    return {}

        return {
            'ID'            : self.obj.GetID().decode(GC_ENC),
            'DateDue'       : self.obj.GetDateDue(),
            'DateOpened'    : self.obj.GetDateOpened(),
            'DatePosted'    : self.obj.GetDatePosted(),

            'Notes'         : (self.obj.GetNotes() or '').decode(GC_ENC),
            'Total'         : self.obj.GetTotal().to_double(),
            'TotalSubtotal' : self.obj.GetTotalSubtotal().to_double(),
            'TotalTax'      : self.obj.GetTotalTax().to_double(),

            'TypeString'    : self.obj.GetTypeString().decode(GC_ENC),

            'Customer'      : Customer(obj=assign_customer[type(self.obj.GetOwner()).__name__](self.obj.GetOwner())).to_dict(),

            'entries'       : [ Entry(obj=entry).to_dict() for entry in self.obj.GetEntries()],
  
            'currency'      : self.obj.GetCurrency().get_mnemonic().decode(GC_ENC),
            'terms'         : Term(obj=self.obj.GetTerms()).to_dict(),
        }

class Tax(BaseAccounting):
    def to_dict(self):
	if self.obj==None:
	    return {}
        return {
            'TaxName': self.obj.GetName().decode(GC_ENC),
        }

class Account(BaseAccounting):
    def to_dict(self):
	if self.obj==None:
	    return {}
        return {
            'Name' : self.obj.GetName().decode(GC_ENC),
            'Code' : self.obj.GetCode().decode(GC_ENC),
            'Notes': (self.obj.GetNotes() or '').decode(GC_ENC),
        }

class Entry(BaseAccounting):

    def to_dict(self):
	if self.obj==None:
	    return {}
        return {
            'Date'             : self.obj.GetDate(),
            'DateEntered'      : self.obj.GetDateEntered(),
            'Action'           : self.obj.GetAction().decode(GC_ENC),
            'Description'      : self.obj.GetDescription().decode(GC_ENC),
            'Notes'            : self.obj.GetNotes().decode(GC_ENC),
            'Quantity'         : self.obj.GetQuantity().to_double(),
            'Price'            : self.obj.GetInvPrice().to_double(),
            'TaxIncluded'      : self.obj.GetInvTaxIncluded(),
            'Taxable'          : self.obj.GetInvTaxable(),
            'TaxTable'         : Tax(obj=self.obj.GetInvTaxTable()).to_dict(),
            'AccountTable'     : Account(obj=self.obj.GetInvAccount()).to_dict(),
            'DocDiscountValue' : self._setGncNumeric(self.obj.GetDocDiscountValue(True,True,False)).to_double(),
            'DocTaxValue'      : self._setGncNumeric(self.obj.GetDocTaxValue(True,True,False)).to_double(),
            'DocValue'         : self._setGncNumeric(self.obj.GetDocValue(True,True,False)).to_double(),
            'BalDiscountValue' : self._setGncNumeric(self.obj.GetBalDiscountValue(True,True)).to_double(),
            'BalTaxValue'      : self._setGncNumeric(self.obj.GetBalTaxValue(True,True)).to_double(),
            'BalValue'         : self._setGncNumeric(self.obj.GetBalValue(True,True)).to_double(),
        }

    def _setGncNumeric(self,val):
       return GncNumeric(val.num, val.denom)

class Customer(BaseAccounting):

    def to_dict(self):
	if self.obj==None:
	     return {}
        return {
             'ID'       : self.obj.GetID().decode(GC_ENC),
             'Name'     : self.obj.GetName().decode(GC_ENC),
             'Notes'    : self.obj.GetNotes().decode(GC_ENC),
             'currency' : self.obj.GetCurrency().get_unique_name().decode(GC_ENC),
         
             'Addr'     : Address(obj=self.obj.GetAddr()).to_dict(),
             'ShipAddr' : Address(obj=self.obj.GetShipAddr()).to_dict(),
        }

class Address(BaseAccounting):

    def to_dict(self):
	if self.obj==None:
	    return {}
        return {
            'Name'  : self.obj.GetName().decode(GC_ENC),
            'Addr1' : self.obj.GetAddr1().decode(GC_ENC),
            'Addr2' : self.obj.GetAddr2().decode(GC_ENC),
            'Addr3' : self.obj.GetAddr3().decode(GC_ENC),
            'Addr4' : self.obj.GetAddr4().decode(GC_ENC),
            'Email' : self.obj.GetEmail().decode(GC_ENC),
            'Fax'   : self.obj.GetFax().decode(GC_ENC),
            'Phone' : self.obj.GetPhone().decode(GC_ENC),
        }

class Term(BaseAccounting):
    def to_dict(self):
        if self.obj==None:
	    return {}

        return {
            'Name'        : self.obj.GetName().decode(GC_ENC),
            'Description' : self.obj.GetDescription().decode(GC_ENC),
            'DueDays'     : self.obj.GetDueDays(),
        }
