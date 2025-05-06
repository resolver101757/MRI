from pydicom import dcmread
from pydicom.uid import generate_uid
ds = dcmread("scan.dcm")
ds.PatientName = "Anonymous"
ds.PatientID = generate_uid()
