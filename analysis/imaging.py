"""Acquisition-side rules, separate from the DWH timing fallback.

The RTPlan-reference flag must be supplied by a validated direct adapter. Neither
a Study match, status New nor a planning-machine label may manufacture this flag.
"""


def classify(*,image_type,modality,task,status=None,device="",dosimeter="",
             has_existing_rtplan_reference=None,reference_image=False):
    result={"class":"unknown","acquisition_qualified":False,"device":device or None,
            "reference_verified":has_existing_rtplan_reference is True}
    if reference_image:
        result["class"]="reference"
    elif image_type=="ImagePI" and modality=="RTIMAGE" and task=="DICOM Service":
        result["class"]=("ExacTrac" if "exactrac" in device.casefold() else
                         {"MINUTE":"kV","MU":"MV"}.get(dosimeter,"unclassified_RTIMAGE"))
        result["acquisition_qualified"]=True
    elif image_type=="Image" and modality=="CT" and task=="DICOM Service":
        result["class"]="CBCT" if has_existing_rtplan_reference is True else "unverified_CT"
        result["acquisition_qualified"]=has_existing_rtplan_reference is True
    return result
