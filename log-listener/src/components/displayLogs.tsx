import { EventLog, Log, formatUnits } from 'ethers'

interface DisplayLogsProps {
  logName: string,
  logs: (EventLog | Log)[]
}

const DisplayLogs = (props: DisplayLogsProps) => {
  const { logName, logs } = props;

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
          </tr>
        </thead>
        <tbody>
          {logs?.map((log, index) => {
            return (
              <tr key={index}>
                <td>{index}</td>
                <td>{log.args![0]}</td>
                <td>{log.args![1]}</td>
                <td>{formatUnits(log.args![2], 0)}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  );
}

export default DisplayLogs
