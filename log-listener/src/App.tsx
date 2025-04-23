import { useState } from 'react'
import { ethers, EventLog, Log } from 'ethers'
import getSigner from './components/getSigner'
import fetchEventLog from './components/fetchEventLog'
import postLog from './components/postLogs'
import DisplayLogs from './components/displayLogs'

function App() {
  const [signer, setSigner] = useState<ethers.Signer>();
  const [contractAddress, setContractAddress] = useState<string>("0xb613051aB06ffcbc5ba8683698e4A14c7C803ede");
  const [myAddress, setMyAddress] = useState<string>("");
  const [postStatus, setPostStatus] = useState<string>("No Post");
  const [sendResults, setSendResults] = useState<(EventLog | Log)[]>([]);
  const [receiveResults, setReceiveResults] = useState<(EventLog | Log)[]>([]);

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
    const logs = await fetchEventLog(contractAddress, myAddress, signer);
    setSendResults(logs.sendLog);
    setReceiveResults(logs.receiveLog);
  }

  const saveLogs = async () => {
    // 送信元のログを保存する
    await postLog("send", contractAddress, sendResults, setPostStatus);
    if (myAddress != "") { return; } // フィルターがない場合は送信先のログのみ保存する
    // 送信先のログを保存する
    await postLog("receive", contractAddress, receiveResults, setPostStatus);
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
          <ul>
            <li>0xAAa87514287CF537fD600BFFdd2e2d65A3A73C3D [https://testnets.opensea.io/ja/collection/zombie-eth]</li>
          </ul>
        </div>
      </div>
      <div>
        <p>{signer != undefined ? "Wallet is connecting" : "Wallet is not Connect"}</p>
        <button onClick={() => getMyAddress()}>Sign</button>
        <button onClick={() => setLogs()}>Get Event Log</button>
      </div>
      <div>
        <p>{postStatus}</p>
        <button onClick={() => saveLogs()}>Save Log</button>
      </div>
      <div>
        <DisplayLogs logName="Send" logs={sendResults} />
        <DisplayLogs logName="Receive" logs={receiveResults} />
      </div>
    </div>
  )
}

export default App
