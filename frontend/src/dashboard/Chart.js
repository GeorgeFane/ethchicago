import * as React from 'react';
import { useTheme } from '@mui/material/styles';
import { LineChart, Line, XAxis, YAxis, Label, ResponsiveContainer } from 'recharts';
import Title from './Title';

// Generate Sales Data
function createData(time, amount) {
  return { time, amount };
}

const data1 = [
  createData('00:00', 0),
  createData('03:00', 300),
  createData('06:00', 600),
  createData('09:00', 800),
  createData('12:00', 1500),
  createData('15:00', 2000),
  createData('18:00', 2400),
  createData('21:00', 2400),
  createData('24:00', undefined),
];

export default function Chart({ data }) {
  const theme = useTheme();
  if (!data) {
    return <div />;
  }

  let rows = [
    // createData('2015/04/21', 100000),
  ]
  for (let [date, amount, price, value] of data.txns) {
    if (value > 0) {
      rows.push(
        createData(date, value)
      )
    }
  }
  rows.push(
    // createData(new Date().toJSON().slice(0, 10), data.txns[data.txns.length - 1][3])
  )
  console.log(rows)

  return (
    <React.Fragment>
      <Title>
        Realized Portfolio Value
      </Title>
      <ResponsiveContainer>
        <LineChart
          data={rows}
          margin={{
            top: 16,
            right: 16,
            bottom: 0,
            left: 24,
          }}
        >
          <XAxis
            dataKey="time"
            stroke={theme.palette.text.secondary}
            style={theme.typography.body2}
          />
          <YAxis
            stroke={theme.palette.text.secondary}
            style={theme.typography.body2}
          />
          <Line
            isAnimationActive={false}
            type="monotone"
            dataKey="amount"
            stroke={theme.palette.primary.main}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </React.Fragment>
  );
}
