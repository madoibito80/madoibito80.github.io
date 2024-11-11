import Arweave from 'arweave';
import { readFileSync } from 'fs';

// You can use any gateway
const arweave = Arweave.init({
  host: 'arweave.net',
  port: 443,
  protocol: 'https',
});

const key = JSON.parse(readFileSync('jwk.json', 'utf8'));
const data = readFileSync('photo.jpeg');
const content_type = 'image/jpeg';

async function sendData(arweave, key, data, content_type) {
  let transaction = await arweave.createTransaction({ data: data }, key);
  transaction.addTag('Content-Type', content_type);

  await arweave.transactions.sign(transaction, key);

  const response = await arweave.transactions.post(transaction);
  console.log(response);
}

sendData(arweave, key, data, content_type);
