from .parse import *
from .models import *
import os
from hashlib import sha256 as hashfunc
from django.db import IntegrityError

def add_project(name, root):
    root = root.rstrip(os.path.sep)
    # remove trailing path separators, e.g. /

    if os.path.isdir(root) and os.path.isabs(root):
        try:
            proj = Project(name=name, root=root)
            proj.save()
        except IntegrityError:
            print("Project with the same name exists")
    else:
        print("Not an absolute dir")

def get_or_create_ident(name, proj):

    try:
        return Ident.objects.get(value=name, project=proj)
    except Ident.DoesNotExist:
        i = Ident(value=name, project=proj)
        i.save()
        return i

def index_project(name):

    try:
        proj = Project.objects.get(name=name)
    except Project.DoesNotExist:
        print("No such project. Abort.")
        return

    if not os.path.isdir(proj.root):
        print("Directory {} does not exist. Abort.".format(proj.root))
        return

    files_to_index = []

    for root, dirs, files in os.walk(proj.root):
        for fp in files:
            abspath = os.path.join(root, fp)
            with open(abspath, "rb") as f:
                hashval = hashfunc(f.read()).hexdigest()
            relpath = abspath.replace(proj.root, "")
            try:
                blob = Blob.objects.get(project=proj, path=relpath)
                if hashval != blob.checksum:
                    # TODO: remove all refs and defs related to this blob
                    files_to_index.append(blob)
                    blob.checksum = hashval
                    blob.save()
            except Blob.DoesNotExist:
                blob = Blob(project=proj, path=relpath, checksum=hashval)
                blob.save()
                files_to_index.append(blob)

    # index definitions

    for blob in files_to_index:
        abspath = proj.root + blob.path
        print("processing defs in {}".format(blob.path))
        for ident, itype, line in parse_defs(abspath):
            ident = get_or_create_ident(ident, proj)
            def_entry = Def(ident=ident, blob=blob, line=line, type=itype)
            def_entry.save()

    # index references

    for blob in files_to_index:
        abspath = proj.root + blob.path
        print("processing refs in {}".format(blob.path))
        for token, tokentype, line in tokenize(abspath):
            try:
                ident = Ident.objects.get(value=token, project=proj)
                ref_entry = Ref(ident=ident, blob=blob, line=line)
                ref_entry.save()
            except Ident.DoesNotExist:
                # ignore tokens that is not in ident
                pass
