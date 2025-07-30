region                    = "us-ashburn-1"
compartment_ocid          = "ocid1.compartment.oc1..exampleuniqueID"
subnet_ocid               = "ocid1.subnet.oc1..exampleuniqueID"
functions = {
    "customer_info" = {
      # This function will be SKIPPED because its source_image is null.
      source_image = null #Change this to image name after uploading image to OCIR
      path = "/customer"
    }
    "place-order" = {
      # This function will be SKIPPED because its source_image is null.
      source_image = null #Change this to image name after uploading image to OCIR
      path = "/order"
    }
}