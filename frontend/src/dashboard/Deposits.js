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

export default function Deposits({ data }) {
  if (!data) {
    return <div />;
  }
  return (
    <React.Fragment>
      <Title>Final Portfolio Value</Title>
      <Typography component="p" variant="h4">
        {formatter.format(data.final)}
      </Typography>
      <Typography color="text.secondary" sx={{ flex: 1 }}>
        on {new Date().toJSON().slice(0, 10)}
      </Typography>
      <div>
        Initial value: {formatter.format(data.initial)}
      </div>
    </React.Fragment>
  );
}
