import React, { useState, useEffect } from 'react';
import {
  healthCheck,
  updateSignText,
  turnOffSign
} from './ApiFunctions/LedSign';
import {
  Spinner,
  Input,
  Button,
  Container,
  Row
} from 'reactstrap';

export default function SignForm(props) {
  const [signHealthy, setSignHealthy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [signData, setSignData] = useState({});
  const [awaitingSignResponse, setAwaitingSignResponse] = useState(false);
  const [requestSuccessful, setRequestSuccessful] = useState();
  const [turnOff, showTurnOff] = useState(false);

  async function handleSend() {
    setAwaitingSignResponse(true);
    const signResponse = await updateSignText(signData);
    setRequestSuccessful(!signResponse.error);
    showTurnOff(!signResponse.error);
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

  async function checkSignHealth() {
    setLoading(true);
    const status = await healthCheck();
    if (status && !status.error) {
      setSignHealthy(true);
      const { message } = status;
      if (message) {
        setSignData({...message});
        showTurnOff(true);
      }
    } else {
      setSignHealthy(false);
    }
    setLoading(false);
  }

  useEffect(() => {
    checkSignHealth();
    if (!Object.keys(signData).length) {
      let copy = signData;
      props.fields.forEach(({ name, additionalProps }) => {
        copy[name] = additionalProps.defaultValue || '';
      });
      setSignData(copy);
    }
    // eslint-disable-next-line
  }, []);

  function renderSignHealth() {
    if (loading) {
      return <Spinner />;
    } else if (signHealthy) {
      return <span className='sign-available'> Sign is up.</span>;
    } else {
      return <span className='sign-unavailable'> Sign is down!</span>;
    }
  }

  function updateSignData(key, value) {
    let copy = signData;
    copy[key] = value;
    setSignData(copy);
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
        {props.fields && props.fields.map((input, index) => {
          const { defaultValue, ...otherProps } = input.additionalProps;
          return (
            <div key={index} className='full-width'>
              <label>{input.title}</label>
              <Input
                disabled={loading || !signHealthy}
                type={input.type}
                defaultValue={signData[input.name] || defaultValue}
                onChange={(e) => updateSignData(input.name, e.target.value)}
                {...otherProps}
              />
            </div>
          );
        })}
        <Row>
          <Button
            id='led-sign-send'
            onClick={handleSend}
            disabled={loading || !signHealthy || awaitingSignResponse}
          >
            {awaitingSignResponse ? <Spinner /> : 'Send'}
          </Button>
          {turnOff && <Button
            id='led-sign-send'
            onClick={
              () => turnOffSign().then(({ error }) => {
                showTurnOff(!!error);
                setSignData({});
                setRequestSuccessful(undefined);
              })
            }
          >
            Turn sign off
          </Button>}
        </Row>
        {renderRequestStatus()}
      </div>
    </div>
  );
}
