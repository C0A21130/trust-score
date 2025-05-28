import { useState, useEffect } from 'react'
import { ethers, EventLog, Log } from 'ethers'
import getSigner from './components/getSigner'
import fetchEventLog from './components/fetchEventLog'
import fetchGas from './components/fetchGas'
import postLog from './components/postLogs'
import DisplayLogs from './components/displayLogs'

function App() {
  const [signer, setSigner] = useState<ethers.Signer>();
  const [contractAddress, setContractAddress] = useState<string>("0xb613051aB06ffcbc5ba8683698e4A14c7C803ede");
  const [myAddress, setMyAddress] = useState<string>("");
  const [postStatus, setPostStatus] = useState<string>("No Post");
  const [sendResult, setSendResult] = useState<{logs: (EventLog | Log)[], price: number[], used: number[]}>({logs: [], price: [], used: []});
  const [receiveResult, setReceiveResult] = useState<{logs: (EventLog | Log)[], price: number[], used: number[]}>({logs: [], price: [], used: []});

  // 自分のアドレスを取得する
  const getMyAddress = async () => {
    const signer = await getSigner();
    setSigner(signer);

    if (signer != undefined) { // サインが成功した場合
      const address = await signer.getAddress();
      setMyAddress(address);
    }
  }

  // イベントログを取得する
  const setLogs = async () => {
    const { sendLog, receiveLog } = await fetchEventLog(contractAddress, myAddress, signer);
    const sendGas = await fetchGas(sendLog, signer?.provider);
    setSendResult({logs: sendLog, price: sendGas.price, used: sendGas.used});
    
    // 送信先のログのみ取得する
    const receiveGas = await fetchGas(receiveLog, signer?.provider);
    setReceiveResult({logs: receiveLog, price: receiveGas.price, used: receiveGas.used});
  }

  const saveLogs = async () => {
    // 送信元のログを保存する
    await postLog("send", contractAddress, sendResult, setPostStatus);
    if (myAddress != "") { return; } // フィルターがない場合は送信先のログのみ保存する
    // 送信先のログを保存する
    await postLog("receive", contractAddress, receiveResult, setPostStatus);
  }

  return (
    <div className="App">
      <div>
        <div>
          <label>
            My Address:
            <input value={myAddress} onChange={(e) => setMyAddress(e.target.value)} />
          </label>
        </div>
        <div>
          <label>
            Contract Address:
            <input value={contractAddress} onChange={(e) => setContractAddress(e.target.value)} />
          </label>
        </div>
        <div>
          <p>Contract Address List</p>
          <ul>
            <li>0xAAa87514287CF537fD600BFFdd2e2d65A3A73C3D [https://testnets.opensea.io/ja/collection/zombie-eth] 433</li>
            <li>0x32F4866B63CaDeD01058540Cff9Bb1fcC05E1cb7 [https://testnets.opensea.io/ja/collection/pokemonpackv1-2] 172</li>
            <li>0xF49af2D8DcaAc24035A2b35429873E4beeB6001E [https://testnets.opensea.io/ja/collection/dreamstack-7] 1</li>
            <li>0x76B50696B8EFFCA6Ee6Da7F6471110F334536321 [https://testnets.opensea.io/ja/collection/foundry-course-nft-6] 203</li>
            <li>0x6dBccC65133635D27AE56B7E3586b6e810d92082 [https://testnets.opensea.io/ja/collection/daffy-panda-ganging-up-1] 756</li>
            <li>0x0D48C738959d5a16108b475a8d0e98d9620BdEB8 [https://testnets.opensea.io/ja/collection/degenz-apes-club] 148</li>
          </ul>
        </div>
      </div>
      <div>
        <p>{signer != undefined ? "Wallet is connecting" : "Wallet is not Connect"}</p>
        <button onClick={() => getMyAddress()}>Sign</button>
        <button onClick={() => setLogs()}>Get Event Log</button>
      </div>
      <div>
        <p>{`Number of logs: ${sendResult.logs.length}`}</p>
        <p>{postStatus}</p>
        <button onClick={() => saveLogs()}>Save Log</button>
      </div>
      <div>
        <DisplayLogs logName="Send" result={sendResult} />
        <DisplayLogs logName="Receive" result={receiveResult} />
      </div>
    </div>
  )
}

export default App
