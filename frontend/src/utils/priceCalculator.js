/**
 * Rounds a number to 2 decimal places
 * @param {number} num - Number to round
 * @returns {string} - Number formatted to 2 decimal places
 */
const addDecimals = (num) => {
  return (Math.round(num * 100) / 100).toFixed(2)
}

/**
 * Calculates the items subtotal from cart items
 * @param {Array} cartItems - Array of items with price and qty
 * @returns {string} - Items price formatted to 2 decimals
 */
const calculateItemsPrice = (cartItems) => {
  const subtotal = cartItems.reduce((acc, item) => acc + item.price * item.qty, 0)
  return addDecimals(subtotal)
}

/**
 * Calculates shipping price based on items price
 * @param {number} itemsPrice - Total items price as string or number
 * @returns {string} - Shipping price formatted to 2 decimals
 */
const calculateShippingPrice = (itemsPrice) => {
  const shippingCost = itemsPrice > 100 ? 0 : 100
  return addDecimals(shippingCost)
}

/**
 * Calculates tax price (15% of items price)
 * @param {number} itemsPrice - Total items price as string or number
 * @returns {string} - Tax price formatted to 2 decimals
 */
const calculateTaxPrice = (itemsPrice) => {
  const taxRate = 0.15
  const tax = Number((taxRate * itemsPrice).toFixed(2))
  return addDecimals(tax)
}

/**
 * Calculates total order price
 * @param {string} itemsPrice - Items price
 * @param {string} shippingPrice - Shipping price
 * @param {string} taxPrice - Tax price
 * @returns {string} - Total price formatted to 2 decimals
 */
const calculateTotalPrice = (itemsPrice, shippingPrice, taxPrice) => {
  const total =
    Number(itemsPrice) + Number(shippingPrice) + Number(taxPrice)
  return total.toFixed(2)
}

/**
 * Validates cart object and its cartItems
 * @param {Object} cart - Cart object to validate
 * @throws {Error} - If cart or cartItems is invalid
 */
const validateCart = (cart) => {
  if (cart === null || cart === undefined) {
    throw new Error('Invalid cart: cart is required and must be an object')
  }

  if (!Array.isArray(cart.cartItems)) {
    throw new Error(
      'Invalid cart: cartItems must be an array'
    )
  }
}

/**
 * Calculates order prices (items, shipping, tax, total)
 * @param {Object} cart - Cart object containing cartItems
 * @returns {Object} - Object with calculated prices { itemsPrice, shippingPrice, taxPrice, totalPrice }
 * @throws {Error} - If cart or cartItems is invalid
 */
const calculatePrices = (cart) => {
  validateCart(cart)

  const itemsPrice = calculateItemsPrice(cart.cartItems)
  const shippingPrice = calculateShippingPrice(itemsPrice)
  const taxPrice = calculateTaxPrice(itemsPrice)
  const totalPrice = calculateTotalPrice(itemsPrice, shippingPrice, taxPrice)

  return {
    itemsPrice,
    shippingPrice,
    taxPrice,
    totalPrice,
  }
}

module.exports = calculatePrices
