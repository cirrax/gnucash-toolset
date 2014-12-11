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

import Query   as Query

import csv

def ExportCustomers(session,csvfile):
    with open(csvfile, 'wb') as csvfile:
      writer=csv.writer(csvfile)

      for customer in Query.getCustomers(session.book):
        row=[]
        row.append(customer.GetID())
        row.append(customer.GetName())

        addr=customer.GetAddr()
        row.append(addr.GetName())
        row.append(addr.GetAddr1())
        row.append(addr.GetAddr2())
        row.append(addr.GetAddr3())
        row.append(addr.GetAddr4())
        row.append(addr.GetPhone())
        row.append(addr.GetFax())
        row.append(addr.GetEmail())

        row.append(customer.GetNotes())

        addr=customer.GetShipAddr()
        row.append(addr.GetName())
        row.append(addr.GetAddr1())
        row.append(addr.GetAddr2())
        row.append(addr.GetAddr3())
        row.append(addr.GetAddr4())
        row.append(addr.GetPhone())
        row.append(addr.GetFax())
        row.append(addr.GetEmail())
   
        writer.writerow(row)

def ExportVendors(session,csvfile):
    with open(csvfile, 'wb') as csvfile:
      writer=csv.writer(csvfile)

      for vendor in Query.getVendors(session.book):
        row=[]
        row.append(vendor.GetID())
        row.append(vendor.GetName())

        addr=vendor.GetAddr()
        row.append(addr.GetName())
        row.append(addr.GetAddr1())
        row.append(addr.GetAddr2())
        row.append(addr.GetAddr3())
        row.append(addr.GetAddr4())
        row.append(addr.GetPhone())
        row.append(addr.GetFax())
        row.append(addr.GetEmail())

        row.append(vendor.GetNotes())

        writer.writerow(row)
