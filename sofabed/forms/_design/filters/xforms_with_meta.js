function (doc, req) {
    if (doc.doc_type == "XFormInstance" && doc.form.meta) {
        return true;
    } else {
        return false;
    }
}