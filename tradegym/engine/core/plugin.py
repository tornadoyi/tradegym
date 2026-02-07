from typing import Optional, Sequence, Dict, Type, Union, ClassVar, List, TypeVar
from .object import TObject, computed_property, PrivateAttr


__all__ = ["Plugin", "PluginManager"]



class Plugin(TObject):

    __PLUGINS__: ClassVar[Dict[str, Type["Plugin"]]] = {}

    Name: ClassVar[str]
    Depends: ClassVar[Sequence[str]] = []

    @computed_property
    def name(self) -> str:
        return self.Name
    
    @property
    def depends(self) -> Sequence[str]:
        return self.Depends
    
    @property
    def manager(self) -> "PluginManager":
        return getattr(self, "__plugin_manager__")
    
    @property
    def installed(self) -> bool:
        return hasattr(self, "__plugin_manager__")

    def setup(self, manager: "PluginManager"):
        setattr(self, "__plugin_manager__", manager)

    def reset(self) -> None: pass
    
    @staticmethod
    def register(type: Type["Plugin"]):
        assert type.Name is not None, ValueError(f"Register plugin type '{type}' have no name field")
        if type.Name in Plugin.__PLUGINS__:
            print(f"override register plugin type '{type.name}'")
        Plugin.__PLUGINS__[type.Name] = type

    @staticmethod
    def make(name: str, **kwargs) -> Optional["Plugin"]:
        cls = Plugin.__PLUGINS__.get(name, None)
        assert cls is not None, ValueError(f"Plugin type '{name}' is not found")
        return cls.from_dict(data=kwargs)


PluginType = TypeVar("T", bound=Plugin)

class PluginManager(TObject):

    _plugins: List[PluginType] = PrivateAttr(default_factory=list)
    _plugin_map: Dict[str, PluginType] = PrivateAttr(default_factory=dict)

    def __init__(self, plugins: Optional[Sequence[Union[Plugin, Dict]]] = None):
        super().__init__()
        plugins = [plg if isinstance(plg, Plugin) else Plugin.make(**plg) for plg in (plugins or [])]
        self.add_plugins(plugins)

    @computed_property
    def plugins(self) -> List[PluginType]:
        return self._plugins
    
    def get_or_create_plugin(self, name: str) -> Plugin:
        plugin = self.find_plugin(name)
        return plugin if plugin is not None else self.add_plugin(name)

    def get_plugin(self, name: str) -> Plugin:
        plugin = self.find_plugin(name)
        assert plugin is not None, ValueError(f"Plugin '{name}' not found")
        return plugin

    def find_plugin(self, name: str) -> Optional[Plugin]:
        return self._plugin_map.get(name, None)

    def add_plugin(self, plugin: Union[str, Plugin]) -> Plugin:
        return self.add_plugins([plugin])[0]

    def has_plugin(self, name: str) -> bool:
        return name in self.plugins

    def add_plugins(self, plugins: Sequence[Union[str, Plugin]]) -> Sequence[Plugin]:
        # initialize plguin map
        plg_map: Dict[str, Plugin] = {}
        for p in plugins:
            assert isinstance(p, (str, Plugin)), TypeError(f"plugin must be a string or a Plugin instance, got {type(p)}")
            pname = p.name if isinstance(p, Plugin) else p
            if pname in plg_map:
                raise ValueError(f"Add repeated plugin '{pname}'")
            plg_map[pname] = p if isinstance(p, Plugin) else Plugin.make(p)

        depends = set()
        def dfs_add(name: str):
            ptype = Plugin.__PLUGINS__.get(name, None)
            assert ptype is not None, ValueError(f"Plugin type '{name}' not found")

            # add dependencies
            for dp_name in ptype.Depends:
                if dp_name in self._plugin_map:
                    continue
                
                # circular check
                if dp_name in depends:
                    raise ValueError(f"Detect circular dependency '{dp_name}' by plugin {name}")
                depends.add(dp_name)

                # add
                dfs_add(dp_name)

            # add plugin
            assert name not in self._plugin_map, ValueError(f"Plugin '{name}' already exists")
            plugin = plg_map.get(name, None)
            plugin = plugin if plugin is not None else Plugin.make(name)
            self._plugins.append(plugin)
            self._plugin_map[name] = plugin
            plugin.setup(self)

        # add plugins
        for name in plg_map.keys():
            if name in self._plugin_map:
                continue
            dfs_add(name)

        return [self.get_plugin(name) for name in plg_map.keys()]
    
    def reset(self):
        for plugin in self.plugins:
            plugin.reset()