import { Dispatch, SetStateAction } from "react";
import { EventLog, Log, formatUnits } from "ethers";
import neo4j, { Session } from "neo4j-driver";

// 送信元のアドレスをノードとして保存する
const saveAddressFrom = async (session: Session, logs: (EventLog | Log)[]) => {
  console.log("start save address from");

  for (const log of logs) {
    await session.executeWrite(async (tx) => {
      // 送信元と送信先のアドレスが重複しないようにする
      const resultFrom = await tx.run(
        'MATCH (u:User {address: $address}) RETURN u',
        {
          address: log.args![0],
        }
      );
      // すでに送信元と送信先のアドレスが保存されている場合は何もしない
      if (resultFrom.records.length > 0) {
        return;
      }

      // 送信元のアドレスを保存する
      await tx.run(
        'CREATE (u:User {address: $address, type: "from"}) RETURN u',
        {
          address: log.args![0],
        }
      );
    });
  };

  console.log("finish save address from");
}

// 送信先のアドレスをノードとして保存する
const saveAddressTo = async (session: Session, logs: (EventLog | Log)[]) => {
  console.log("start save address to");

  for (const log of logs) {
    await session.executeWrite(async (tx) => {
      // 送信先のアドレスが重複しないようにする
      const resultTo = await tx.run(
        'MATCH (u:User {address: $address}) RETURN u',
        {
          address: log.args![1],
        }
      );

      // すでに送信先のアドレスが保存されている場合は何もしない
      if (resultTo.records.length > 0) {
        return;
      }

      // 送信先のアドレスを保存する
      await tx.run(
        'CREATE (u:User {address: $address, type: "to"}) RETURN u',
        {
          address: log.args![1],
        }
      );
    });
  }

  console.log("finish save address to");
}   

// 送信元と送信先のアドレスを結ぶリレーションを保存する
const saveRelation = async (contractAddress: string, session: Session, logs: (EventLog | Log)[]) => {
  console.log("start save relation");

  for (const log of logs) {
    await session.executeWrite(async (tx) => {
      await tx.run(
        'MATCH (from:User {address: $from}), (to:User {address: $to}) CREATE (from)-[:TRANSFER {tokenId: $tokenId, contractAddress: $contractAddress}]->(to)',
        {
          from: log.args![0],
          to: log.args![1],
          tokenId: formatUnits(log.args![2], 0),
          contractAddress: contractAddress,
        }
      );
    });
  }

  console.log("finish save relation");
}

// グラフデータベースにログを保存する
const postLogs = async (name: String, contractAddress: string, logs: (EventLog | Log)[], setStatus: Dispatch<SetStateAction<string>>) => {
  // Neo4jにログを保存する
  const driver = neo4j.driver("bolt://10.203.92.71:7687");
  let session: Session = driver.session();

  setStatus(`【${name}】Start post logs`);

  try {
    // 送信元のアドレスをノードとして保存する
    await saveAddressFrom(session, logs);
    setStatus(`【${name}】Saved Address From`);

    // 送信先のアドレスをノードとして保存する
    await saveAddressTo(session, logs);
    setStatus(`【${name}】Saved Address To`);

    // 送信元と送信先のアドレスを結ぶリレーションを保存する
    await saveRelation(contractAddress, session, logs);
    setStatus(`【${name}】Saved Relation`);

  } finally {
    await session.close();
    setStatus(`【${name}】Finish post logs`);
  }
  
}

export default postLogs;
