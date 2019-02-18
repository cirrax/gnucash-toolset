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

import logging
import jinja2

import Session
import Invoice
import Export
import Copy
import JsonImport

def gnucash_toolset():
   commands={
           'csv-customers'     :  csv_customer,
           'csv-vendors'       :  csv_vendors,
           'create-copy'       :  create_copy,
           'get-bill'          :  get_bill,
           'json-import'       :  json_import,
            }

   parser=ArgArgumentParser(description='Gnucash toolset to export/manipulate gnucash data', formatter_class=RawTextHelpFormatter)
   parser.add_argument('command',
                        choices=set(commands),
                        help="""Commands to execute:
csv-customers  : Create a CSV file with all customers. Ready to import with gnucash.
csv-vendors    : Create a CSV file with all vendors. Ready to import with gnucash.
create-copy    : Create a copy of gnucash data. Data copied are: Accounts, Customers, Vendors.
                 Data NOT copied: Bookings, Invoices, Bills, Transactions.
                 Data to be copied, but not yet implemented: Terms, Taxes, Employees, Jobs, Options.
                 This can be used to create a new file after closing period.
                 Hint: use xml:///path/file for destination file ...
copy-opening   : copy opening-amounts from another gnucash instance. (Not yet implemented).
get-bill       : Export a bill from gnucash (in_file) into a jinja template.
json-import    : Imports a json file (in_file) into gnucash (out_file).
""",)
   parser.add_argument('in_file', help='uri to Path/file for input')
   parser.add_argument('out_file', help='uri to Path/file for output')
   parser.add_argument('--loglevel', help='Log level', default='INFO')
   parser.add_argument('--template', help='jinja2 template to use for get-bill')
   parser.add_argument('--invoice', help='invoice ID to usefor get-bill')
   parser.add_argument('--date_format', help='Date format in JSON parts/files.', default='%Y-%m-%dT%H:%M:%S')
   args=parser.parse_args()

   logging.basicConfig(level=getattr(logging, args.loglevel.upper()))

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

def get_bill(args):
  session=Session.startSession(file=args.in_file,  ignore_lock=True)
  invoice=Invoice.Invoice(session.book.InvoiceLookupByID(args.invoice))

  env = jinja2.Environment(loader=jinja2.FileSystemLoader(args.template.rpartition('/')[0]))
  env.filters['date'] = Invoice.date_filter
  env.filters['fromjson'] = lambda x: Invoice.fromjson_filter(x, date_format=args.date_format)
  env.filters['isorting'] = lambda x,y,z: Invoice.isorting_filter(x, y, z)

  template=env.get_template(args.template.rpartition('/')[2])

  if '-' == args.out_file:
      print template.render(invoice=invoice.to_dict()).encode('utf-8')
  else:
      with open(args.out_file, "wb") as f:
          f.write(template.render(invoice=invoice.to_dict()).encode('utf-8'))

  Session.endSession(session)

def json_import(args):
  session=Session.startSession(file=args.out_file,  ignore_lock=False)
  ji=JsonImport.JsonImport(file=args.in_file, date_format=args.date_format)
  ji.post(session.book)
  session.save()
  Session.endSession(session)

