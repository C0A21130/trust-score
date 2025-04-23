import { ethers, Contract } from 'ethers';

const abi = [
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "address",
        name: "from",
        type: "address",
      },
      {
        indexed: true,
        internalType: "address",
        name: "to",
        type: "address",
      },
      {
        indexed: true,
        internalType: "uint256",
        name: "tokenId",
        type: "uint256",
      },
    ],
    name: "Transfer",
    type: "event",
  },
];

/**
 *  Eventのログを取得する
 * @param contractAddress コントラクトアドレス
 * @param myAddress 自分のアドレス
 * @param signer サインするためのSigner
 * @returns 送信先と受け取り先のログ
 */ 
const fetchEventLog = async (contractAddress: string, myAddress: string, signer: ethers.Signer | undefined) => {
  const contract = new Contract(contractAddress, abi, signer);

  // アドレスを指定しない場合は全てのログを取得する
  if (myAddress == "") { // もしアドレスを指定しないでログを取得する場合
    const logs = await contract.queryFilter("Transfer");
    console.log(logs);
    return {sendLog: logs, receiveLog: logs};
  }
  
  // 送信先のアドレスを指定してログを取得する
  const sendFilter = contract.filters.Transfer(myAddress, null, null);
  const sendlogs = await contract.queryFilter(sendFilter);
  // 受け取り先のアドレスを指定してログを取得する
  const receiveFilter = contract.filters.Transfer(null, myAddress, null);
  const receiveLogs = await contract.queryFilter(receiveFilter);
  return {sendLog: sendlogs, receiveLog: receiveLogs};
}

export default fetchEventLog;
