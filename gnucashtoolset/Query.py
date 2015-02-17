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

import gnucash
import gnucash.gnucash_business

from gnucash import \
     Session, GnuCashBackendException, \
     ERR_BACKEND_LOCKED, ERR_FILEIO_FILE_NOT_FOUND

from gnucash import \
    QOF_QUERY_AND, \
    QOF_QUERY_OR, \
    QOF_QUERY_NAND, \
    QOF_QUERY_NOR, \
    QOF_QUERY_XOR

from gnucash import \
    QOF_STRING_MATCH_NORMAL, \
    QOF_STRING_MATCH_CASEINSENSITIVE

from gnucash import \
    QOF_COMPARE_LT, \
    QOF_COMPARE_LTE, \
    QOF_COMPARE_EQUAL, \
    QOF_COMPARE_GT, \
    QOF_COMPARE_GTE, \
    QOF_COMPARE_NEQ

def getJobs(book):

    query = gnucash.Query()
    query.search_for('gncJob')
    query.set_book(book)
    jobs = []

    for result in query.run():
         jobs.append(gnucash.gnucash_business.Job(instance=result))

    query.destroy()

    return jobs

def getCustomers(book):

    query = gnucash.Query()
    query.search_for('gncCustomer')
    query.set_book(book)
    customers = []

    for result in query.run():
         customers.append(gnucash.gnucash_business.Customer(instance=result))

    query.destroy()

    return customers

def getVendors(book):

    query = gnucash.Query()
    query.search_for('gncVendor')
    query.set_book(book)
    vendors = []

    for result in query.run():
         vendors.append(gnucash.gnucash_business.Vendor(instance=result))

    query.destroy()

    return vendors


#res=getCustomers(session.book)


