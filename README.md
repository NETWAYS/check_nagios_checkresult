check_nagios_checkresult
========================

Icinga plugin to retrieve status from Nagios CGIs.

## Usage

The plugin behaves and returns the same output and return code, as any other plugin would.

```
./check_nagios_checkresult.py \
  --cgi https://nagios.example.com/nagios/cgi-bin \
  -u nagios -p test \
  -H localhost -S service
```

This queries data from the URL:

```
https://nagios.example.com/nagios/cgi-bin/statusjson.cgi?query=service&hostname=host&servicedescription=service
```

## License

Copyright (C) 2020 [NETWAYS GmbH](info@netways.de)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
