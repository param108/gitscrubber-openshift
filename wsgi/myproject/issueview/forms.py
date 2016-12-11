from django import forms

class Repoform(forms.Form):
  repository=forms.CharField(max_length=100)

class Boardform(forms.Form):
  board=forms.CharField(max_length=100)

class Userform(forms.Form):
  username=forms.CharField(max_length=100)

class Filterform(forms.Form):
  release=forms.CharField(max_length=50,required=False)
  assigned=forms.CharField(max_length=50,required=False)
  repository=forms.CharField(max_length=50,required=False)
  status=forms.CharField(max_length=50,required=False)
  labels=forms.CharField(max_length=200,required=False)

FILTER_OPTIONS = ["release","assigned","repository","status","labels"]
