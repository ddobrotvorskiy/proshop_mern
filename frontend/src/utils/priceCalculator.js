/**
 * Rounds a number to 2 decimal places
 * @param {number} num - Number to round
 * @returns {string} - Number formatted to 2 decimal places
 */
const addDecimals = (num) => {
  return (Math.round(num * 100) / 100).toFixed(2)
}

/**
 * Calculates order prices (items, shipping, tax, total)
 * @param {Object} cart - Cart object containing cartItems, itemsPrice
 * @returns {Object} - Object with calculated prices { itemsPrice, shippingPrice, taxPrice, totalPrice }
 */
export const calculatePrices = (cart) => {
  const itemsPrice = addDecimals(
    cart.cartItems.reduce((acc, item) => acc + item.price * item.qty, 0)
  )

  const shippingPrice = addDecimals(itemsPrice > 100 ? 0 : 100)
  const taxPrice = addDecimals(Number((0.15 * itemsPrice).toFixed(2)))
  const totalPrice = (
    Number(itemsPrice) +
    Number(shippingPrice) +
    Number(taxPrice)
  ).toFixed(2)

  return {
    itemsPrice,
    shippingPrice,
    taxPrice,
    totalPrice,
  }
}

export default calculatePrices
