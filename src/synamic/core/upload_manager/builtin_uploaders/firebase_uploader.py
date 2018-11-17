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
        output_dir = self.__synamic.system_settings['dirs.outputs.outputs']
        output_cdir = path_tree.create_dir_cpath(output_dir)
        extras_dir = self.__synamic.system_settings['dirs.configs.configs']
        extras_cdir = path_tree.create_dir_cpath(extras_dir)
        firebase_json_cfile = extras_cdir.join('firebase/firebase.json', is_file=True)
        firebase_rc_cfile = extras_cdir.join('firebase/.firebaserc', is_file=True)

        # checking for firebase files
        if not firebase_json_cfile.exists() or not firebase_rc_cfile.exists():
            print(f'Error: firebase.json and .firebaserc file must exists in extras: '
                  f'{firebase_json_cfile.abs_path} {firebase_rc_cfile.abs_path}', file=sys.stderr)
            return False
        root_site_settings = self.__synamic.sites.root_site.settings

        # firebase project name
        firebase_projce_name = os.getenv('FIREBASE_PROJECT_NAME', None)
        if firebase_projce_name is None:
            firebase_projce_name = root_site_settings.get('firebase.FIREBASE_PROJECT_NAME', None)
        if firebase_projce_name is None:
            print(f'Firebase project_name is not specified in environment, neither in site settings under firebase key', file=sys.stderr)
            return False

        # firebase ci token
        firebase_ci_token = os.getenv('FIREBASE_CI_TOKEN', None)
        if firebase_ci_token is None:
            firebase_ci_token = root_site_settings.get('firebase.FIREBASE_CI_TOKEN', None)

        if firebase_ci_token is None:
            print(f'FIREBASE_CI_TOKEN not found in environment, neither in settings', file=sys.stderr)
            return False

        # build first
        print(f'Building the sites before uploading')
        build_succeeded = self.__synamic.sites.build()
        if not build_succeeded:
            print(f'Building failed. Not uploading. See error log.', file=sys.stderr)
            return False

        # write config files
        with firebase_json_cfile.open('r', encoding='utf-8') as fr:
            json_text = fr.read()
            rendered_json = self.__synamic.render_string_template(
                json_text,
                # public_dir_name=output_cdir.basename <- was trouble maker as uploading is done by cd'ing into _outputs
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
            retcode = subprocess.call(command, shell=True)
        finally:
            os.chdir(cwd_bk)
            # TODO: remove firebase.json & .firebaserc from outputs dir after work is done? Yes, privacy/security issue.
        if retcode != 0:
            print(f'Upload was not successful, returned with code {retcode}', file=sys.stderr)
            return False
        else:
            return True
