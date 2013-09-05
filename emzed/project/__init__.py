

def init(name=None):
    from ..core.config import global_config
    from ..gui import DialogBuilder, showWarning
    project_home = global_config.get("project_home").strip()
    if not project_home:
        raise Exception("no project folder configured. please run emzed.config.edit()")

    from ..core.packages import create_package_scaffold, check_name
    if name is None:
        while True:
            name = DialogBuilder().addString("Package Name")\
                    .addInstruction("valid package names contain a-z, 0-9 and '_' and start " \
                    "with a lower case letter").show()
            complaint = check_name(name)
            if not complaint:
                break
            showWarning(complaint)

    import os
    folder = os.path.join(project_home, name)
    try:
        create_package_scaffold(folder, name)
    except Exception ,e:
        showWarning(str(e))
        return

    __builtins__["___activate_%s" % name] = lambda : activate(name)
    print
    print "project scaffold created, enter emzed.project.activate() to start working on it."
    print
    print "please edit setup.py for your needs"
    os.chdir(folder)
    try:
        # should be set during ipython shell startup
        open_in_spyder(os.path.join(folder, "setup.py"))
    except:
        pass


def _get_active_project():
    proj = __builtins__.get("__emzed_project__")
    if not proj:
        raise Exception("no active project set")
    return proj


def _set_active_project(project):
    if project is not None:
        import os
        project = os.path.abspath(project)
    __builtins__["__emzed_project__"] = project


def _run_setup_py_develop(uninstall=False):
    #subprocess runnint "setup.py develop [-u]"  kills socket for monitor thread !!!, so:
    import sys, os

    from setuptools.command.develop import develop
    from setuptools import Distribution

    import sys
    sys.path.insert(0, ".")
    import setup
    sys.path.pop(0)

    d = Distribution(dict(name=setup.PKG_NAME,
                          packages=[setup.PKG_NAME],
                          version=setup.VERSION_STRING,
                          entry_points=setup.ENTRY_POINTS))
    d.script_name = "setup.py"
    cmd = develop(d)
    cmd.user = 1
    cmd.uninstall = uninstall
    cmd.ensure_finalized()
    import site
    cmd.install_dir = site.USER_SITE
    cmd.user = 1
    cmd.run()


def _install_builtins():
    #return
    __builtins__["___deactivate"] = deactivate
    __builtins__["___run_tests"] = run_tests
    __builtins__["___upload"] = upload
    __builtins__["___remove_from_package_store"] = remove_from_package_store
    __builtins__["___list_versions"] = list_versions


def _uninstall_builtins():
    del __builtins__["___deactivate"]
    del __builtins__["___run_tests"]
    del __builtins__["___upload"]
    del __builtins__["___remove_from_package_store"]
    del __builtins__["___list_versions"]


def deactivate():
    ap = _get_active_project()
    import subprocess, sys
    subprocess.call("python setup.py develop -u", shell=True, stderr=sys.__stderr__, stdout=sys.__stdout__)

    _set_active_project(None)
    _uninstall_builtins()

    try:
        import os
        os.chdir(__builtins__["__old_home"])
    except:
        pass
    
    from ..core.config import global_config
    global_config.set_("last_active_project", "")
    global_config.store()


def run_tests():
    ap = _get_active_project()
    import os
    import subprocess, sys
    path = os.path.join(ap, "tests")
    subprocess.call("py.test %s" % path, shell=True, stderr=sys.__stderr__, stdout=sys.__stdout__)


def upload():
    ap = _get_active_project()
    from ..core.packages import upload_to_emzed_store
    upload_to_emzed_store(ap)


def remove_from_package_store(version_string):
    ap = _get_active_project()
    from ..core.packages import delete_from_emzed_store
    import os
    print
    ok = raw_input("ARE YOU SURE TO DELTED VERSION %s OF %s FROM PACKAGE STORE (Y/N) ? ")
    if ok != "Y":
        print
        print "ABORTED"
        return
    __, name = os.path.split(ap)
    delete_from_emzed_store(name, version_string)


def list_versions():
    ap = _get_active_project()
    from ..core.packages import list_packages_from_emzed_store
    import os
    __, name = os.path.split(ap)
    versions = [v for (n, v) in list_packages_from_emzed_store() if n==name]
    assert len(versions) <= 1, "INTERNAL ERROR"
    print
    if not versions:
        print "PACKAGE NOT FOUND ON EMZED PACKAGE STORE"
    else:
        print "VERSIONS ON EMZED PACKAGE STORE:"
        print
        versions = versions[0]
        for v in versions:
            print "   %s.%s.%s" % v


def list_projects():
    import os
    from ..core.packages import is_project_folder
    from ..core.config   import global_config
    project_home = global_config.get("project_home").strip()
    #projects = [os.path.join(project_home, f) for ]
    result = [f for f in os.listdir(project_home) \
                 if is_project_folder(os.path.join(project_home, f))]
    return result


def activate(name=None):
    import os
    from ..core.packages import is_project_folder
    __builtins__["__old_home"] = os.getcwd() # ipapi.get().IP.home_dir
    if name is None:
        if is_project_folder("."):
            _set_active_project(os.getcwd())
        else:
            raise Exception("either cd to emzed project before you call emzed.project.activate, "\
                    "or provide a project name or a full path")
    else:
        if is_project_folder(name):
            _set_active_project(name)
            os.chdir(name)
        else:
            from ..core.config import global_config
            project_home = global_config.get("project_home").strip()
            path_in_project_home = os.path.join(project_home, name)
            if is_project_folder(path_in_project_home):
                _set_active_project(path_in_project_home)
                os.chdir(path_in_project_home)
            else:
                raise Exception("'%s' is not a valid project folder" % name)

    _install_builtins()

    import subprocess, sys
    subprocess.call("python setup.py develop", shell=True, stderr=sys.__stderr__, stdout=sys.__stdout__)

    from ..core.config import global_config
    global_config.set_("last_active_project", name)
    global_config.store()


__builtins__["___activate"] = activate
__builtins__["___init"] = init
__builtins__["___list_projects"] = list_projects

for _n in list_projects():
    __builtins__["___activate_%s" % _n] = lambda _n=_n: activate(_n)


from ..core.config import global_config
last_project  = global_config.get("last_active_project")
project_home  = global_config.get("project_home")

if last_project:
    #activate(last_project) # does not work, crashes on win maybe bcause starting pythonin subprocess
    import os
    path_in_project_home = os.path.join(project_home, last_project)
    _set_active_project(path_in_project_home)
    os.chdir(path_in_project_home)
    _install_builtins()
    del os

del last_project, global_config, project_home

