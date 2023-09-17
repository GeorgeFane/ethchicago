import * as React from 'react';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';
import Title from './Title';

function preventDefault(event) {
  event.preventDefault();
}

const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',

  // These options are needed to round to whole numbers if that's what you want.
  //minimumFractionDigits: 0, // (this suffices for whole numbers, but will print 2500.10 as $2,500.1)
  //maximumFractionDigits: 0, // (causes 2500.99 to be printed as $2,501)
});

export default function Risk({ data }) {
  if (!data) {
    return <div />;
  }
  return (
    <React.Fragment>
      <Title>Sharpe Ratio</Title>
      <Typography component="p" variant="h4">
        {Math.round(data.sharpe * 10000) / 10000}
      </Typography>
      <Typography color="text.secondary" sx={{ flex: 1 }}>
      System Quality Number {Math.round(data.sqn * 100) / 100}
      </Typography>
      <div>
        Variable Weighted Return: {Math.round(data.vwr * 100) / 100}
      </div>
    </React.Fragment>
  );
}
