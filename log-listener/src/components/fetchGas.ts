import { ethers, formatUnits, Provider, EventLog, Log } from 'ethers';

/**
 * トランザクション履歴からガス代を取得する
 * @param logs ログの配列
 * @param provider プロバイダー
 * @returns ガス価格
*/
const fetchGas = (logs: (EventLog | Log)[], provider: (Provider | null | undefined)) => {
  let txHash = "";
  let txReceipt: ethers.TransactionReceipt | null;
  const gasPrices: number[] = [];
  const gasUseds: number[] = [];
  
  if (provider == null) { return { price: [], used: [] } } // プロバイダーが取得できない場合は空の配列を返す
  // ログの数だけトランザクションを取得する
  logs.map(async (log) => {
    txHash = log.transactionHash;
    txReceipt = await provider.getTransactionReceipt(txHash);
    if (txReceipt == null) { return { price: [], used: [] } } // トランザクションが取得できない場合は空の配列を返す
    const gasPrice = Number(formatUnits(txReceipt.gasPrice, 'gwei'));
    const gasUsed = Number(formatUnits(txReceipt.gasUsed, 'gwei'));
    gasPrices.push(gasPrice);
    gasUseds.push(gasUsed);

    // ガス価格とガス量を表示する
    // console.log(`設定されたガス価格: ${gasPrice} gwei`);
    // console.log(`使用されたガス価格: ${gasUsed} gwei`);
  });

  return { price: gasPrices, used: gasUseds };
}

export default fetchGas;
