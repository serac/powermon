from settings import ROOT_URL

def root_url(context):
  """Adds the ROOT_URL setting to the template processing context."""
  return {'ROOT_URL': ROOT_URL}