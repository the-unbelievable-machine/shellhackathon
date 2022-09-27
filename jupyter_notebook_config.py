import os
from subprocess import check_call


def post_save(model, os_path, contents_manager):
    """
    Post-save hook for converting notebooks to .py scripts
    """
    if model['type'] != 'notebook':
        return  # only do this for notebooks

    cwd, nb_name = os.path.split(os_path)
    script_name = f'{nb_name[:-6]}.py'
    # print(cwd, nb_name, script_name)
    cmd = f'cat {nb_name} | nbstripout | jupyter-nbconvert --to python --stdin --stdout > {script_name}'
    check_call([cmd], cwd=cwd, shell=True)


c.FileContentsManager.post_save_hook = post_save
