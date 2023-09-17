import * as React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import SendIcon from '@mui/icons-material/Send';
import Stack from '@mui/material/Stack';

export default function FormPropsTextFields({ handleClick, setText }) {
  return (
    <Box
      sx={{
        '& .MuiTextField-root': { m: 1, width: '100%' },
      }}
      noValidate
      autoComplete="off"
    >
      <Stack direction="row" spacing={2}>
        <TextField
          id="filled-helperText"
          label="Describe your trading strategy"
          helperText="ex. Buy and hold"
          margin="normal"
          fullWidth
          onChange={event => {
            setText(event.target.value)
          }}
        />
        <Button
          variant="contained"
          endIcon={<SendIcon />}
          style={{ height: 40, marginTop: 14 }}
          onClick={handleClick}
        >
          Send
        </Button>
      </Stack>
    </Box>
  );
}
