import pytest

import asyncio
import pytest

from asynctest import TestCase as AsyncTestCase, mock

from aries_cloudagent.askar.profile import AskarProfile
from aries_cloudagent.config.injection_context import InjectionContext

from .. import profile as test_module
from ...core.profile import Profile, ProfileSession
from ...core.in_memory import InMemoryProfile


class TestProfile(AsyncTestCase):
    @mock.patch("aries_cloudagent.askar.store.AskarOpenStore")
    async def test_init_success(self, AskarOpenStore):
        askar_profile = AskarProfile(
            AskarOpenStore,
        )

        assert askar_profile.opened == AskarOpenStore

    @mock.patch("aries_cloudagent.askar.store.AskarOpenStore")
    async def test_remove_success(self, AskarOpenStore):
        openStore = AskarOpenStore
        context = InjectionContext() 
        wallet_id = "wallet_id"
        context.settings = {
            "multitenant.wallet_type": "askar-profile",
            "wallet.id": wallet_id
        }
        askar_profile = AskarProfile(
            openStore,
            context
        )
        remove_profile_stub = asyncio.Future()
        remove_profile_stub.set_result(True)
        openStore.store.remove_profile.return_value = remove_profile_stub

        await askar_profile.remove()
        
        openStore.store.remove_profile.assert_called_once_with(wallet_id)

    @mock.patch("aries_cloudagent.askar.store.AskarOpenStore")
    async def test_remove_profile_not_removed_if_wallet_type_not_askar_profile(self, AskarOpenStore):
        openStore = AskarOpenStore
        context = InjectionContext() 
        context.settings = {
            "multitenant.wallet_type": "basic"
        }
        askar_profile = AskarProfile(
            openStore,
            context
        )
        
        await askar_profile.remove()
        
        openStore.store.remove_profile.assert_not_called()

    @pytest.mark.asyncio
    async def test_profile_manager_transaction(self):

        with mock.patch(
            "aries_cloudagent.askar.profile.AskarProfile"
        ) as AskarProfile:
            askar_profile = AskarProfile(None, True)
            askar_profile_transaction = mock.MagicMock()
            askar_profile.store.transaction.return_value = askar_profile_transaction
            askar_profile.context.settings.get.return_value = "walletId"

            transactionProfile = test_module.AskarProfileSession(askar_profile, True)

            assert transactionProfile._opener == askar_profile_transaction
            askar_profile.context.settings.get.assert_called_once_with("wallet.id")
            askar_profile.store.transaction.assert_called_once_with("walletId")

    @pytest.mark.asyncio
    async def test_profile_manager_store(self):

        with mock.patch(
            "aries_cloudagent.askar.profile.AskarProfile"
        ) as AskarProfile:
            askar_profile = AskarProfile(None, False)
            askar_profile_session = mock.MagicMock()
            askar_profile.store.session.return_value = askar_profile_session
            askar_profile.context.settings.get.return_value = "walletId"

            sessionProfile = test_module.AskarProfileSession(askar_profile, False)

            assert sessionProfile._opener == askar_profile_session
            askar_profile.context.settings.get.assert_called_once_with("wallet.id")
            askar_profile.store.session.assert_called_once_with("walletId")
