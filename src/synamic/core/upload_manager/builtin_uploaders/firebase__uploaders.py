import sys
import os
import re
import subprocess
import datetime
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


class FireBaseUploader:
    def __init__(self, synamic):
        self.__synamic = synamic

    def upload(self):
        path_tree = self.__synamic.path_tree
        output_dir = self.__synamic.default_data.get_syd('dirs')['outputs.outputs']
        output_cdir = path_tree.create_dir_cpath(output_dir)
        extras_dir = self.__synamic.default_data.get_syd('dirs')['configs.configs']
        extras_cdir = path_tree.create_dir_cpath(extras_dir)
        firebase_json_cfile = extras_cdir.join('firebase/firebase.json', is_file=True)
        firebase_rc_cfile = extras_cdir.join('firebase/.firebaserc', is_file=True)

        # checking for firebase files
        if not firebase_json_cfile.exists() or not firebase_rc_cfile.exists():
            print(f'Error: firebase.json and .firebaserc file must exists in extras: '
                  f'{firebase_json_cfile.abs_path} {firebase_rc_cfile.abs_path}')
            return False
        root_site_settings = self.__synamic.sites.root_site.object_manager.get_site_settings()
        firebase_projce_name = root_site_settings.get('firebase.project_name', None)
        if firebase_projce_name is None:
            print(f'Firebase project_name is not specified in site settings under firebase key')
            return False

        # firebase ci token
        firebase_ci_token = os.getenv('FIREBASE_CI_TOKEN', None)
        if firebase_ci_token is None:
            firebase_ci_token = root_site_settings.get('firebase.FIREBASE_CI_TOKEN', None)

        if firebase_ci_token is None:
            print(f'FIREBASE_CI_TOKEN not found in environment, neither in settings')
            return False

        # build first
        print(f'Building the sites before uploading')
        build_succeeded = self.__synamic.sites.build()
        if not build_succeeded:
            print(f'Building failed. Not uploading. See error log.')
            return False

        # write config files
        with firebase_json_cfile.open('r', encoding='utf-8') as fr:
            json_text = fr.read()
            rendered_json = self.__synamic.render_string_template(
                json_text,
                public_dir_name=output_cdir.basename
            )
            with output_cdir.join(firebase_json_cfile.basename, is_file=True).open('w', encoding='utf-8') as fw:
                fw.write(rendered_json)

        with firebase_rc_cfile.open('r', encoding='utf-8') as fr:
            rc_text = fr.read()
            rendered_rc = self.__synamic.render_string_template(
                rc_text,
                project_name=firebase_projce_name
            )
            with output_cdir.join(firebase_rc_cfile.basename, is_file=True).open('w', encoding='utf-8') as fw:
                fw.write(rendered_rc)

        # upload
        cur_dt = datetime.datetime.utcnow().strftime('%y-%m-%d %H:%M:%S')
        command = ['firebase', 'deploy', '--only', 'hosting', '-m', f'Deploy @ {cur_dt}',
                   '--token', f'{firebase_ci_token}']
        cwd_bk = os.getcwd()
        os.chdir(output_cdir.abs_path)
        try:
            cp = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        finally:
            os.chdir(cwd_bk)
        sys.stdout.write(cp.stdout)
        sys.stderr.write(ansi_escape.sub('', cp.stderr))
        if cp.returncode != 0:
            print(f'Upload was not successful, returned with code {cp.returncode}')
