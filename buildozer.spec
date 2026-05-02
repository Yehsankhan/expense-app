[app]
title = ExpenseApp
package.name = expenseapp
package.domain = org.yourname

source.dir = .
source.include_exts = py,kv,png,jpg,db

version = 1.0

requirements = python3,kivy==2.2.1,kivymd,matplotlib,pandas,reportlab

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
