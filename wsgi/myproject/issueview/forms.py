from django import forms

class Repoform(forms.Form):
  repository=forms.CharField(max_length=100)

class Boardform(forms.Form):
  board=forms.CharField(max_length=100)

class Userform(forms.Form):
  username=forms.CharField(max_length=100)

class Filterform(forms.Form):
  release=forms.CharField(max_length=50)
  assigned=forms.CharField(max_length=50)
  repository=forms.CharField(max_length=50)
  status=forms.CharField(max_length=50)

FILTER_OPTIONS = ["release","assigned","repository","status"]
