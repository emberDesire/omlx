import ast, asyncio, json, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
P=Path(__file__).resolve().parents[1]/'omlx'

def load_functions(filename,names,env):
    tree=ast.parse((P/('admin/routes.py' if filename=='routes.py' else filename)).read_text())
    nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in names]
    for n in nodes:
        n.decorator_list=[]
        n.returns=None
        n.args.defaults=[]
        if n.name=='_preflight_memory_projection':n.args.defaults=[ast.Constant(False)]
        for a in n.args.args:a.annotation=None
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),filename,'exec'),env)
    return env

class IdleTests(unittest.IsolatedAsyncioTestCase):
    async def test_pool_atomic_activity_checks(self):
        class Lock:
            async def __aenter__(self):pass
            async def __aexit__(self,*a):pass
        entries={name:SimpleNamespace(engine=object(),is_loading=False,is_pinned=name=='pinned',in_use=1 if name=='leased' else 0,last_access=0) for name in ['idle','pinned','leased','active','loading','cold']}
        entries['loading'].is_loading=True;entries['cold'].engine=None
        unloaded=[]
        async def unload(mid):unloaded.append(mid)
        pool=SimpleNamespace(_lock=Lock(),_entries=entries,_entry_has_active_requests=lambda e:e is entries['active'],_unload_engine=unload)
        e={'time':SimpleNamespace(time=lambda:1)};load_functions('engine_pool.py',set(),e)
        tree=ast.parse((P/'engine_pool.py').read_text());node=next(n for n in ast.walk(tree) if isinstance(n,ast.AsyncFunctionDef) and n.name=='unload_if_idle_unpinned');node.returns=None
        for a in node.args.args:a.annotation=None
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'pool','exec'),e)
        for name in entries: self.assertEqual(await e['unload_if_idle_unpinned'](pool,name),name=='idle')
        self.assertEqual(unloaded,['idle'])
    async def test_route_excludes_target_and_reports_skips(self):
        calls=[]
        async def unload(mid):calls.append(mid);return mid=='idle'
        pool=SimpleNamespace(_entries={'target':1,'idle':1,'busy':1},unload_if_idle_unpinned=unload,resolve_model_id=lambda mid,settings:'target')
        e={'_get_engine_pool':lambda:pool,'_get_settings_manager':None};load_functions('routes.py',{'evict_idle_models'},e)
        result=await e['evict_idle_models'](SimpleNamespace(exclude_model_id='alias'),True)
        self.assertEqual(calls,['idle','busy']);self.assertEqual(result,{'status':'ok','evicted':['idle'],'skipped':['busy']})

if __name__=='__main__':unittest.main()
