==========================
Web Widget Digital Address
==========================

Widget to auto-format digital address values.

Usage
=====
Inputs with this widget set will automatically be formatted as digital address if valid. Otherwise, the original input will be maintained.

Note: Precede your input values with an asterisk to opt out of the automatic format.

Development
===========
Set the widget attribute to 'digital_address' on character fields so they are automatically formatted as digital address.

Known Issues
============
Automatic formatting might only sometimes be desired, and we will need a way to permanently mark the record so as not to format the input. We have chosen not to implement a mixin to limit the boilerplate required by the developer to implement this widget.
