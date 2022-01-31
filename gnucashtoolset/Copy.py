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

from gnucash import Account as Account
from gnucash import Transaction, Split
from gnucash.gnucash_business import Customer, Vendor, Address, Job
import datetime

from gnucash.gnucash_core_c import \
    ACCT_TYPE_ASSET, ACCT_TYPE_BANK, ACCT_TYPE_CASH, ACCT_TYPE_CHECKING, \
    ACCT_TYPE_CREDIT, ACCT_TYPE_EQUITY, ACCT_TYPE_EXPENSE, ACCT_TYPE_INCOME, \
    ACCT_TYPE_LIABILITY, ACCT_TYPE_MUTUAL, ACCT_TYPE_PAYABLE, \
    ACCT_TYPE_RECEIVABLE, ACCT_TYPE_STOCK, ACCT_TYPE_ROOT, ACCT_TYPE_TRADING


from . import Query as Query

def CopyOptions(session, session_new):
    print('CopyOptions: to be implemented')

def CopyAccounts(session, session_new):
    commodtable = session_new.book.get_table()
    openbalance = _recursiveCopyAccounts(session, session_new, session.book.get_root_account(), session_new.book.get_root_account(), commodtable)

    # now let's create an opening balance
    trans = Transaction(session_new.book)
    trans.BeginEdit()
    trans.SetCurrency(session_new.book.get_table().lookup('CURRENCY', 'CHF'))
    date=datetime.date.today()
    trans.SetDate(date.day, date.month, date.year)
    trans.SetDescription('opening balance')

    for ob in openbalance:
        split=Split(session_new.book)
        split.SetAccount(ob['account'])
        split.SetValue(ob['balance'])
        split.SetAmount(ob['balance'])
        split.SetMemo(ob['account'].GetName())
        split.SetParent(trans)

    trans.CommitEdit()

def _recursiveCopyAccounts(session, session_new, account, account_new, commodtable):
    attributes=['Hidden' , 'ReconcileChildrenStatus', 'TaxUSCode', 'Code', 'LastNum', 'TaxUSCopyNumber',
                'Color', 'TaxUSPayerNameSource', 'Name', 'Type', 'NonStdSCU', 'Description', 'Notes', 
                'SortOrder', 'Filter', 'Placeholder', 'TaxRelated' ]
    openbalance = []
    for acc in account.get_children():
         acc_new=Account(session_new.book)
         account_new.append_child(acc_new)
         openbalance = openbalance + _recursiveCopyAccounts(session, session_new, acc, acc_new, commodtable)

    for attrib in attributes:
          getattr(account_new, 'Set' + attrib)(getattr(account, 'Get' + attrib)() )

    # copy commodity
    orig_commodity = account.GetCommodity()
    if orig_commodity:
       namespace = orig_commodity.get_namespace()
       mnemonic = orig_commodity.get_mnemonic()
       new_commodity = commodtable.lookup(namespace, mnemonic)
       account_new.SetCommodity(new_commodity)

    # save balance for creating opening
    if account_new.GetType() in [ 
         ACCT_TYPE_ASSET, ACCT_TYPE_BANK,
         ACCT_TYPE_CASH, ACCT_TYPE_CREDIT,
         ACCT_TYPE_ASSET, ACCT_TYPE_LIABILITY,
         ACCT_TYPE_STOCK, ACCT_TYPE_MUTUAL,
         ACCT_TYPE_EQUITY, ACCT_TYPE_RECEIVABLE,
         ACCT_TYPE_PAYABLE, ACCT_TYPE_TRADING ]:

      fb = account.GetBalance()
      if fb.num() != 0:
        openbalance.append( {
            'account': account_new,
            'balance': account.GetBalance(),
        })
    return openbalance


def CopyCustomers(session,session_new):
   attributes=['Active',
               'Discount',
               'TaxIncluded', 'Credit', 'Notes']
   # 'TaxTableOverride', 'Terms', 'TaxTable'
   # These attributes are not copied, and are lost.
   # you can include them to coppy and manually copy XML from the old XML
   # file to the new one !
   # Tables to copy are: <gnc:GncBillTerm version="2.0.0">
   # and <gnc:GncTaxTable version="2.0.0">
   # The TaxTable needs to be edited afterwards, since the account reference changed.

   commodtable = session_new.book.get_table()
   for customer in Query.getCustomers(session.book):
       commod = commodtable.lookup('CURRENCY', customer.GetCurrency().get_mnemonic())

       customer_new = Customer(session_new.book, customer.GetID(), commod, customer.GetName())
       for attrib in attributes:
          getattr(customer_new, 'Set' + attrib)(getattr(customer, 'Get' + attrib)() )

       for job in customer.GetJoblist(True):
          job_old = Job(instance=job)
          if job_old.GetActive() == True:
             job_new = Job(book=session_new.book, id=job_old.GetID(), owner=customer_new, name=job_old.GetName())

       _CopyAddress(customer.GetAddr(),customer_new.GetAddr())
       _CopyAddress(customer.GetShipAddr(),customer_new.GetShipAddr())
   

def CopyVendors(session,session_new):
   attributes=['TaxTableOverride', 'Active',
               'TaxIncluded', 'Notes', 'TaxTable' ]

   commodtable = session_new.book.get_table()
   for vendor in Query.getVendors(session.book):
       commod = commodtable.lookup('CURRENCY', vendor.GetCurrency().get_mnemonic())

       vendor_new = Vendor(session_new.book, vendor.GetID(), commod, vendor.GetName())
       for attrib in attributes:
          getattr(vendor_new, 'Set' + attrib)(getattr(vendor, 'Get' + attrib)() )

       _CopyAddress(vendor.GetAddr(),vendor_new.GetAddr())

def _CopyAddress(address, address_new ):
    address_new.SetName(address.GetName())
    address_new.SetAddr1(address.GetAddr1())
    address_new.SetAddr2(address.GetAddr2())
    address_new.SetAddr3(address.GetAddr3())
    address_new.SetAddr4(address.GetAddr4())
    address_new.SetPhone(address.GetPhone())
    address_new.SetFax(address.GetFax())
    address_new.SetEmail(address.GetEmail())


def CopyScheduled(session,session_new):
    print('CopyScheduled: to be implemented')

def CopyTerms(session,session_new):
    print('CopyTerms: to be implemented')

def CopyTaxes(session,session_new):
    print('CopyTaxes: to be implemented')
