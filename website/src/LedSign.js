import React, { useState, useEffect } from 'react';
import { healthCheck, updateSignText } from './ApiFunctions/LedSign';
import { Spinner, Input, Button, Container } from 'reactstrap';
import './led-sign.css';

function LedSign(props) {
  const [signHealthy, setSignHealthy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState('');
  const [brightness, setBrightness] = useState(50);
  const [scrollSpeed, setScrollSpeed] = useState(10);
  const [backgroundColor, setBackgroundColor] = useState('#000000');
  const [textColor, setTextColor] = useState('#ffffff');
  const [borderColor, setBorderColor] = useState('#000000');
  const [awaitingSignResponse, setAwaitingSignResponse] = useState(false);
  const [requestSuccessful, setRequestSuccessful] = useState();
  const inputArray = [
    {
      title: 'Sign Text:',
      placeholder: 'Enter Text',
      value: text,
      type: 'text',
      onChange: e => setText(e.target.value),
      maxLength: '50'
    },
    {
      title: 'Background Color',
      value: backgroundColor,
      type: 'color',
      onChange: e => setBackgroundColor(e.target.value)
    },
    {
      title: 'Text Color',
      value: textColor,
      type: 'color',
      onChange: e => setTextColor(e.target.value)
    },
    {
      title: 'Border Color',
      value: borderColor,
      type: 'color',
      onChange: e => setBorderColor(e.target.value)
    },
    {
      title: 'Brightness:',
      value: brightness,
      min: '25',
      max: '75',
      step: '1',
      type: 'range',
      onChange: e => setBrightness(e.target.value)
    },
    {
      title: 'Scroll Speed:',
      id: 'scroll-speed',
      value: scrollSpeed,
      min: '1',
      max: '20',
      step: '1',
      type: 'range',
      onChange: e => setScrollSpeed(e.target.value)
    }
  ];

  async function handleSend() {
    setAwaitingSignResponse(true);
    const signResponse = await updateSignText({
      text,
      brightness,
      scrollSpeed,
      backgroundColor,
      textColor,
      borderColor,
      email: 'props.user.email',
      firstName: 'props.user.firstName'
    });
    setRequestSuccessful(!signResponse.error);
    setAwaitingSignResponse(false);
  }

  function renderRequestStatus() {
    if (awaitingSignResponse || requestSuccessful === undefined) {
      return <></>;
    } else if (requestSuccessful) {
      return <p className='sign-available'>Sign successfully updated!</p>;
    } else {
      return (
        <p className='sign-unavailable'>The request failed. Try again later.</p>
      );
    }
  }
  useEffect(() => {
    async function checkSignHealth() {
      setLoading(true);
      const status = await healthCheck();
      if (status && !status.error) {
        setSignHealthy(true);
        const { responseData } = status;
        if (responseData && responseData.text) {
          setText(responseData.text);
          setBrightness(responseData.brightness);
          setScrollSpeed(responseData.scrollSpeed);
          setBackgroundColor(responseData.backgroundColor);
          setTextColor(responseData.textColor);
          setBorderColor(responseData.borderColor);
        }
      } else {
        setSignHealthy(false);
      }
      setLoading(false);
    }
    checkSignHealth('props.user.firstName');
    // eslint-disable-next-line
  }, [])

  function renderSignHealth() {
    if (loading) {
      return <Spinner />;
    } else if (signHealthy) {
      return <span className='sign-available'> Sign is up.</span>;
    } else {
      return <span className='sign-unavailable'> Sign is down!</span>;
    }
  }

  return (
    <div>
      <div className='sign-wrapper'>
        <Container>
          <h1 className='sign-status'>
            Sign Status:
            {renderSignHealth()}
          </h1>
        </Container>
        {inputArray.map((input, index) => {
          return (
            <div key={index} className='full-width'>
              <label>{input.title}</label>
              <Input disabled={loading || !signHealthy} {...input} />
            </div>
          );
        })}
        <Button
          id='led-sign-send'
          onClick={handleSend}
          disabled={loading || !signHealthy || awaitingSignResponse}
        >
          {awaitingSignResponse ? <Spinner /> : 'Send'}
        </Button>
        {renderRequestStatus()}
      </div>
    </div>
  );
}

export default LedSign;
