"""API for registering contracts for external libraries."""
from dataclasses import dataclass
from inspect import Signature, signature
import inspect
from typing import Callable, Dict, Optional


class ContractRegistrationError(Exception):
    pass


@dataclass
class Contract:
    pre: Optional[Callable[..., bool]]
    post: Optional[Callable[..., bool]]
    sig: Optional[Signature]


REGISTERED_CONTRACTS: Dict[Callable, Contract] = {}


def _verify_signatures(fn: Callable, contract: Contract) -> None:
    """Verify the provided signatures (including signatures of `pre` and `post`)."""
    sig = signature(fn)
    params = list(sig.parameters.keys())
    if contract.sig:
        sig_params = list(contract.sig.parameters.keys())
        if sig_params != params:
            raise ContractRegistrationError(
                f"Malformed signature for function {fn.__name__}. Expected parameters: {params}, found: {sig_params}"
            )
    fn_params = set(params)
    if contract.pre:
        pre_params = set(signature(contract.pre).parameters.keys())
        if not pre_params <= fn_params:
            raise ContractRegistrationError(
                f"Malformated precondition for function {fn.__name__}. Unexpected arguments: {pre_params - fn_params}"
            )
    if contract.post:
        post_params = set(signature(contract.post).parameters.keys())
        fn_params.add("result")
        fn_params.add("OLD")
        if not post_params <= fn_params:
            raise ContractRegistrationError(
                f"Malformated postcondition for function {fn.__name__}. Unexpected parameters: {post_params - fn_params}."
            )


def register_contract(
    fn: Callable,
    *,
    pre: Optional[Callable[..., bool]] = None,
    post: Optional[Callable[..., bool]] = None,
    sig: Optional[Signature] = None,
) -> None:
    """
    Register a contract for the given function.

    :param fn: The function to add a contract for.
    :param pre: The preconditon which should hold when entering the function.
    :param post: The postcondition which should hold when returning from the function.
    :param sig: If provided, CrossHair will use this signature for the function.\
        Usefull for manually providing type annotation.
    :raise: `ContractRegistrationError` if the registered contract is malformed.
    """
    if inspect.ismethod(fn):
        raise ContractRegistrationError(
            f"You registered the bound method {fn}. You should register the unbound function of the class {fn.__self__.__class__} instead."  # type: ignore
        )
    contract = Contract(pre, post, sig)
    _verify_signatures(fn, contract)
    REGISTERED_CONTRACTS[fn] = contract


def get_contract(fn: Callable) -> Optional[Contract]:
    """
    Get the contract associated to the given function, it the function was registered.

    :param fn: The function to retrieve the contract for.
    :return: The contract associated with the function or None if the function was not registered.
    """
    return REGISTERED_CONTRACTS.get(fn)
