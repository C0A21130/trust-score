import { EventLog, Log, formatUnits } from 'ethers'
import { useEffect } from 'react';

interface DisplayLogsProps {
  logName: string,
  result: {
    logs: (EventLog | Log)[],
    price: number[],
    used: number[]
  }
}

const DisplayLogs = (props: DisplayLogsProps) => {
  const { logName, result } = props;

  return (
    <div>
      <h1>{`${logName} Log`}</h1>
      <table>
        <thead>
          <tr>
            <th>No</th>
            <th>From</th>
            <th>To</th>
            <th>TokenId</th>
            <th>Price</th>
            <th>Used</th>
          </tr>
        </thead>
        <tbody>
          {result?.logs.map((log, index) => {
            return (
              <tr key={index}>
                <td>{index}</td>
                <td>{log.args![0]}</td>
                <td>{log.args![1]}</td>
                <td>{formatUnits(log.args![2], 0)}</td>
                <td>{result.price[index]}</td>
                <td>{result.used[index]}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  );
}

export default DisplayLogs
