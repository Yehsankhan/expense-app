[app]

# App identity
title = Expense App
package.name = expenseapp
package.domain = org.example

# Source files
source.dir = .
source.include_exts = py,kv,png,jpg

# Main file
source.main = main.py

# Version
version = 1.0

# Requirements (IMPORTANT)
requirements = python3,kivy,kivymd,reportlab

# Orientation
orientation = portrait

# Permissions (optional safe default)
android.permissions = INTERNET

# Android settings
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Build settings
log_level = 2
warn_on_root = 1

[buildozer]

log_level = 2
