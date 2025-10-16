function badlyFormatted(x: number, y: number) {
  const result = x + y;
  return result;
}

interface User {
  name: string;
  age: number;
  email: string;
}

const user: User = { name: "John", age: 30, email: "john@example.com" };

const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map((n) => n * 2);

if (user.age > 18) {
  console.log("Adult");
} else {
  console.log("Minor");
}

export { badlyFormatted, user, numbers, doubled };
