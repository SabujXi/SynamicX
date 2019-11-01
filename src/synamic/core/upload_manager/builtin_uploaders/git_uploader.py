import sys
import os
import re
import subprocess
import datetime
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


class GitUploader:
    def __init__(self, synamic):
        self.__synamic = synamic

    def upload(self):
        try:
            import pygit2
        except ImportError:
            print("Error: pygit2 is not installed - try again after installing with: pip install pygit2")
            return False

        path_tree = self.__synamic.path_tree
        output_dir = self.__synamic.system_settings['dirs.outputs.outputs']
        output_cdir = path_tree.create_dir_cpath(output_dir)
        extras_dir = self.__synamic.system_settings['dirs.configs.configs']
        extras_cdir = path_tree.create_dir_cpath(extras_dir)

        root_site_settings = self.__synamic.sites.root_site.settings

        git_url = root_site_settings.get('git.GIT_URL', None)
        if git_url is None:
            print(f'GIT_URL not found in settings', file=sys.stderr)
            return False

        git_user = root_site_settings.get('git.GIT_USER', None)
        if git_user is None:
            print(f'GIT_USER not found in settings', file=sys.stderr)
            return False

        git_email = root_site_settings.get('git.GIT_EMAIL', None)
        if git_user is None:
            print(f'GIT_EMAIL not found in settings', file=sys.stderr)
            return False

        # git dev key/ci token/password
        git_pass = os.getenv('GIT_PASS', None)
        if git_pass is None:
            git_pass = root_site_settings.get('git.GIT_PASS', None)
            if git_pass is None:
                print(f'GIT_PASS not found in environment, neither in settings', file=sys.stderr)
                return False

        git_branch = root_site_settings.get('git.GIT_BRANCH', 'master')

        # clone the repository in the build dir.
        self.__synamic.sites.clean_output_dir()  # clean the dir for cloning.

        # clone
        output_dir = self.__synamic.system_settings['dirs.outputs.outputs']
        output_cdir = self.__synamic.path_tree.create_dir_cpath(output_dir)
        if not output_cdir.exists():
            output_cdir.makedirs()
        output_abs_path = output_cdir.abs_path

        repo = pygit2.clone_repository(git_url, output_abs_path)

        repo.index.add_all()

        # commiter_signature = pygit2.repository
        #
        # user = repo.default_signature
        # tree = repo.index.write_tree()
        # commit = repo.create_commit('HEAD',
        #                             ,
        #                             user,
        #                             'Version %d of test.txt on %s' % (
        #                             version, os.path.basename(os.path.normpath(repo.workdir))),
        #                             tree,
        #                             parent)
        # Apparently the index needs to be written after a write tree to clean it up.
        # https://github.com/libgit2/pygit2/issues/370
        repo.index.write()



        # build first
        print(f'Building the sites before uploading')
        build_succeeded = self.__synamic.sites.build()
        if not build_succeeded:
            print(f'Building failed. Not uploading. See error log.', file=sys.stderr)
            return False

        # write config files
        with git_json_cfile.open('r', encoding='utf-8') as fr:
            json_text = fr.read()
            rendered_json = self.__synamic.render_string_template(
                json_text,
                # public_dir_name=output_cdir.basename <- was trouble maker as uploading is done by cd'ing into _outputs
            )
            with output_cdir.join(git_json_cfile.basename, is_file=True).open('w', encoding='utf-8') as fw:
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
                   '--token', f'{git_pass}']
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
