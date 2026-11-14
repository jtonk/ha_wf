"""Regression tests for the bundled card resource registration."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'custom_components' / 'windfinder'
pkg = types.ModuleType('wf_frontend_test')
pkg.__path__ = [str(PACKAGE)]
sys.modules[pkg.__name__] = pkg
spec = importlib.util.spec_from_file_location(pkg.__name__ + '.frontend', PACKAGE / 'frontend.py')
frontend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frontend)

class FrontendTests(unittest.IsolatedAsyncioTestCase):
    async def register(self, items):
        resources = MagicMock(spec=frontend.lovelace.resources.ResourceStorageCollection)
        resources.async_get_info = AsyncMock()
        resources.async_items.return_value = items
        resources.async_update_item = AsyncMock()
        resources.async_create_item = AsyncMock()
        hass = MagicMock()
        hass.http.async_register_static_paths = AsyncMock()
        hass.data = {frontend.lovelace.DOMAIN: types.SimpleNamespace(resources=resources)}
        with patch.object(frontend, 'async_get_integration', AsyncMock(return_value=types.SimpleNamespace(version='0.8.1'))):
            await frontend.async_register_card(hass)
        resources.async_get_info.assert_awaited_once()
        return resources

    async def test_existing_current_resource_uses_stored_type_field(self):
        resources = await self.register([{'id':'card','url':frontend.CARD_PATH+'?v=0.8.1','type':'module'}])
        resources.async_update_item.assert_not_awaited()
        resources.async_create_item.assert_not_awaited()

    async def test_old_resource_updates_through_ws_res_type_field(self):
        resources = await self.register([{'id':'card','url':frontend.CARD_PATH+'?v=0.8.0','type':'module'}])
        resources.async_update_item.assert_awaited_once_with('card',{'res_type':'module','url':frontend.CARD_PATH+'?v=0.8.1'})

    async def test_incorrect_resource_type_is_repaired(self):
        resources = await self.register([{'id':'card','url':frontend.CARD_PATH+'?v=0.8.1','type':'css'}])
        resources.async_update_item.assert_awaited_once()

    async def test_missing_resource_is_created(self):
        resources = await self.register([])
        resources.async_create_item.assert_awaited_once_with({'res_type':'module','url':frontend.CARD_PATH+'?v=0.8.1'})

if __name__ == '__main__':
    unittest.main()
