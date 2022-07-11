# -*- coding: utf-8 -*-
import argparse
import json
import sys

from ansible import constants as C
from ansible import context
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager


# Create a callback object so we can capture the output
class ResultsCollector(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = dict(detail_msg=[])
        self.host_unreachable = dict(detail_msg=[])
        self.host_failed = dict(detail_msg=[])

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable["result"] = "failed"
        self.host_unreachable[result._host.get_name()] = {
            'unreachable': result._result.get('unreachable'),
            'msg': result._result.get('msg'),
        }

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok["result"] = "success"
        host = result._host.get_name()
        results = []
        if not host in self.host_failed.keys():
            self.host_ok[host] = ["localhost"]

        if 'results' in result._result.keys():
            results = result._result['results']
        else:
            results.append(result._result)
        # msg for success
        self.host_ok["detail_msg"].append(result._result)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed["result"] = "failed"
        host = result._host.get_name()
        results = []
        if not host in self.host_failed.keys():
            self.host_failed[host] = ["localhost"]

        if 'results' in result._result.keys():
            results = result._result['results']
        else:
            results.append(result._result)
        # msg for failed
        self.host_failed["detail_msg"].append(result._result)

# deal with command line args
def get_extra_vars_command():
    parser = argparse.ArgumentParser(description="this is ansible-play-book")
    parser.add_argument("-r", "--role",
                    dest="target_role",
                    help="required,ansible role object",
                    action='store')

    parser.add_argument("-k", "--key",
                    dest="target_key",
                    help="option,var_files key",
                    action='store')

    parser.add_argument("-v", "--value",
                    dest="target_value",
                    help="option,var_files value",
                    action='store')

    parser.add_argument("-t", "--tag",
                    dest="target_tag",
                    help="option,ansible task tag",
                    action='store')

    args = parser.parse_args()
    target_role = args.target_role if args.target_role else None
    target_key = args.target_key if args.target_key else None
    target_value = args.target_value if args.target_value else None
    target_tag = args.target_tag if args.target_tag else None
    if target_role:
        extra_vars["role"] = target_role
    if target_key and target_value:
        extra_vars["k"] = target_key
        extra_vars["v"] = target_value
    if target_tag:
        extra_tags.append(target_tag)
    return extra_vars,extra_tags

# deal with json args
def get_extra_vars_json():
    extra_dict = json.loads(sys.argv[1])
    try:
        target_role = extra_dict["role"]
        extra_vars["role"] = target_role
    except Exception as err:
        print ('{"result":"failed","msg":"needs key_value argument role"}')
    if extra_dict.get("key") and extra_dict.get("value"):
        extra_vars["k"] = extra_dict["key"]
        extra_vars["v"] = extra_dict["value"]
    else:
        extra_vars["k"] = "temp_k"
        extra_vars["v"] = "temp_v"
    if extra_dict.get("tags"):
        extra_tags.append(extra_dict.get("tags"))
    return extra_vars,extra_tags

def main(extra_vars,extra_tags):
    # config cli args
    context.CLIARGS = ImmutableDict(connection='smart',
                                    module_path='',
                                    forks=5,
                                    become=True,
                                    become_method='sudo',
                                    become_user='root',
                                    check=False,
                                    diff=False,
                                    verbosity=0,
                                    remote_user='root',
                                    syntax=False,
                                    start_at_task=None,
                                    tags=extra_tags
                                    )
    # false for checking host
    C.HOST_KEY_CHECKING = False

    loader = DataLoader()
    passwords = dict(conn_pass='juminfo2016')
    inventory = InventoryManager(loader=loader, sources='/etc/ansible/hosts')
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    # args value
    variable_manager._extra_vars = extra_vars
    # defined play-book
    books = ['/opt/smc/ansible/site.yml']
    callback = ResultsCollector()
    play = PlaybookExecutor(playbooks=books, variable_manager=variable_manager, loader=loader,
                          passwords=passwords,inventory=inventory)
    play._tqm._stdout_callback = callback
    try:
        result = play.run()
    except Exception as e:
        print (json.dumps({"result": "success","detail_msg":"unknow error"}))
        sys.exit(1)

    # return result
    failed_result = callback.host_failed.get("result")
    unreachable_result = callback.host_unreachable.get("result")
    if not failed_result and not unreachable_result:
        print (json.dumps(callback.host_ok))
        sys.exit(0)
    elif failed_result:
        print (json.dumps(callback.host_failed))
        sys.exit(1)
    else:
        print (json.dumps(callback.host_unreachable))
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Usage: --help')
        exit(0)
    # defined extra_vars dict and tags list
    extra_vars = dict()
    extra_tags = list()
    if len(sys.argv) == 2 and sys.argv[1] != "--help":
        extra_vars,extra_tags = get_extra_vars_json()
    else:
        extra_vars,extra_tags = get_extra_vars_command()

    main(extra_vars,extra_tags)


