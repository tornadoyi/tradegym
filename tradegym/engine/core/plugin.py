from typing import Optional, Sequence, Dict, Type, Union, ClassVar, List, TypeVar, Any
from .object import TObject, computed_field, Field, field_validator, writable


__all__ = ["Plugin", "PluginManager"]



class Plugin(TObject):

    __PLUGINS__: ClassVar[Dict[str, Type["Plugin"]]] = {}

    Name: ClassVar[str]
    Depends: ClassVar[Sequence[str]] = []

    @computed_field
    @property
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
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.__PLUGINS__[cls.Name] = cls

    def setup(self, manager: "PluginManager"):
        setattr(self, "__plugin_manager__", manager)

    def reset(self) -> None: pass
    
    @staticmethod
    def make(name: str, **kwargs) -> Optional["Plugin"]:
        cls = Plugin.__PLUGINS__.get(name, None)
        assert cls is not None, ValueError(f"Plugin type '{name}' is not found")
        return cls.deserialize(data=kwargs)


PluginType = TypeVar("T", bound=Plugin)

class PluginManager(TObject):

    plugins: List[PluginType] = Field(default_factory=list)
    plugin_map: Dict[str, PluginType] = Field(default_factory=dict, exclude=True)

    def __init__(self, plugins: Optional[Sequence[Union[Plugin, Dict]]] = None):
        super().__init__()
        self.add_plugins(plugins)

    @field_validator('plugins', mode='plain')
    @classmethod
    def _deserialize_plugins(cls, v: Any):
        return [plg if isinstance(plg, Plugin) else Plugin.make(**plg) for plg in v]
        

    def get_or_create_plugin(self, name: str) -> Plugin:
        plugin = self.find_plugin(name)
        return plugin if plugin is not None else self.add_plugin(name)

    def get_plugin(self, name: str) -> Plugin:
        plugin = self.find_plugin(name)
        assert plugin is not None, ValueError(f"Plugin '{name}' not found")
        return plugin

    def find_plugin(self, name: str) -> Optional[Plugin]:
        return self.plugin_map.get(name, None)

    @writable
    def add_plugin(self, plugin: Union[str, Plugin]) -> Plugin:
        return self.add_plugins([plugin])[0]

    def has_plugin(self, name: str) -> bool:
        return name in self.plugins

    @writable
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
                if dp_name in self.plugin_map:
                    continue
                
                # circular check
                if dp_name in depends:
                    raise ValueError(f"Detect circular dependency '{dp_name}' by plugin {name}")
                depends.add(dp_name)

                # add
                dfs_add(dp_name)

            # add plugin
            assert name not in self.plugin_map, ValueError(f"Plugin '{name}' already exists")
            plugin = plg_map.get(name, None)
            plugin = plugin if plugin is not None else Plugin.make(name)
            self.plugins.append(plugin)
            self.plugin_map[name] = plugin
            plugin.setup(self)

        # add plugins
        for name in plg_map.keys():
            if name in self.plugin_map:
                continue
            dfs_add(name)

        return [self.get_plugin(name) for name in plg_map.keys()]
    
    def reset(self):
        for plugin in self.plugins:
            plugin.reset()