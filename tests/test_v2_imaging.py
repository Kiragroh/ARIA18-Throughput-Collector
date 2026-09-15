def test_imaging_acquisition_classification_requires_semantic_evidence():
    import importlib.util
    assert importlib.util.find_spec("analysis.imaging") is not None
    from analysis.imaging import classify
    assert classify(image_type="Image",modality="CT",task="DICOM Service",status="New",
                    has_existing_rtplan_reference=None)["class"]=="unverified_CT"
    assert classify(image_type="Image",modality="CT",task="DICOM Service",status="New",
                    has_existing_rtplan_reference=True)["class"]=="CBCT"
    assert classify(image_type="ImagePI",modality="RTIMAGE",task="DICOM Service",
                    device="ExacTrac Xray",dosimeter="MU")["class"]=="ExacTrac"
    assert classify(image_type="ImagePI",modality="RTIMAGE",task="DICOM Service",
                    dosimeter="MINUTE")["class"]=="kV"
    assert classify(image_type="ImagePI",modality="RTIMAGE",task="DICOM Service",
                    dosimeter="MU",reference_image=True)["class"]=="reference"
