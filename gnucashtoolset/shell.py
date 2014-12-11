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

from argparse import ArgumentParser    as ArgArgumentParser
from argparse import RawTextHelpFormatter as RawTextHelpFormatter

import Session as Session
import Export as Export
import Copy as Copy

def gnucash_toolset():
   commands={
           'csv-customers'     :  csv_customer,
           'csv-vendors'       :  csv_vendors,
           'create-copy'       :  create_copy,
            }

   parser=ArgArgumentParser(description='Gnucash toolset to export/manipulate gnucash data', formatter_class=RawTextHelpFormatter)
   parser.add_argument('command',
                        choices=set(commands),
                        help="""Commands to execute:
csv-customers  : Create a CSV file with all customers. Ready to import with gnucash.
csv-vendors    : Create a CSV file with all vendors. Ready to import with gnucash.
create-copy    : Create a copy of gnucash data. Data copied are: Accounts, Customers, Vendors.
                 Data NOT copied: Bookings, Invoices, Bills.
                 Data to be copied, but not yet implemented: Terms, Taxes, Employees, Options.
                 This can be used to create a new file after closing period.
copy-opening   : copy opening-amounts from another gnucash instance. (Not yet implemented).
""",)
   parser.add_argument('in_file', help='Path to gnucash file to take out values')
   parser.add_argument('out_file', help='Path/file for output')
   args=parser.parse_args()

   commands[args.command](args=args)

def csv_customer(args):
  session=Session.startSession(file=args.in_file,  ignore_lock=True)
  Export.ExportCustomers(session, csvfile=args.out_file)
  Session.endSession(session)

def csv_vendors(args):
  session=Session.startSession(file=args.in_file,  ignore_lock=True)
  Export.ExportVendors(session, csvfile=args.out_file)
  Session.endSession(session)

def create_copy(args):

  session=Session.startSession(file=args.in_file,  ignore_lock=True)
  session_new=Session.startSession(file=args.out_file, ignore_lock=False, is_new=True)

  Copy.CopyAccounts(session,session_new)
  Copy.CopyTerms(session,session_new)
  Copy.CopyTaxes(session,session_new)
  Copy.CopyCustomers(session,session_new)
  Copy.CopyVendors(session,session_new)

  session_new.save()
  Session.endSession(session)
  Session.endSession(session_new)


