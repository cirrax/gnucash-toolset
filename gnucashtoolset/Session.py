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

from gnucash import \
     Session, GnuCashBackendException, \
     ERR_BACKEND_LOCKED, ERR_FILEIO_FILE_NOT_FOUND


def startSession(file, ignore_lock=False, is_new=False):
    try:
       return Session( file, ignore_lock=ignore_lock, is_new=is_new)
    except GnuCashBackendException, backend_exception:
       assert( ERR_FILEIO_FILE_NOT_FOUND in backend_exception.errors)

def endSession(session):
    session.end()
    session.destroy()

