FROM node:18-alpine

WORKDIR /app

COPY webapp/package.json .
# COPY webapp/package-lock.json . 

RUN npm install

COPY webapp/ .

CMD ["npm", "run", "dev", "--", "--host"]
