const calculatePrices = require('../priceCalculator')

describe('calculatePrices', () => {
  describe('Happy path - standard cart', () => {
    it('should calculate prices correctly for normal single item', () => {
      const cart = {
        cartItems: [{ price: 50, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '50.00',
        shippingPrice: '100.00',
        taxPrice: '7.50',
        totalPrice: '157.50',
      })
    })

    it('should calculate prices correctly for multiple items', () => {
      const cart = {
        cartItems: [
          { price: 30, qty: 2 },
          { price: 25, qty: 1 },
        ],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '85.00',
        shippingPrice: '100.00',
        taxPrice: '12.75',
        totalPrice: '197.75',
      })
    })

    it('should calculate prices correctly for high value cart (free shipping)', () => {
      const cart = {
        cartItems: [{ price: 150, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '150.00',
        shippingPrice: '0.00',
        taxPrice: '22.50',
        totalPrice: '172.50',
      })
    })

    it('should handle exact 100 threshold (still charged shipping)', () => {
      const cart = {
        cartItems: [{ price: 100, qty: 1 }],
      }
      const result = calculatePrices(cart)

      // This asserts current buggy behavior. Correct would be: shippingPrice = '0.00' for itemsPrice > 100
      // The condition is itemsPrice > 100, so 100 does NOT trigger free shipping
      expect(result).toEqual({
        itemsPrice: '100.00',
        shippingPrice: '100.00',
        taxPrice: '15.00',
        totalPrice: '215.00',
      })
    })

    it('should handle just under 100 threshold (paid shipping)', () => {
      const cart = {
        cartItems: [{ price: 99.99, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '99.99',
        shippingPrice: '100.00',
        taxPrice: '15.00',
        totalPrice: '214.99',
      })
    })

    it('should handle decimal prices with rounding', () => {
      const cart = {
        cartItems: [
          { price: 19.99, qty: 3 },
          { price: 14.50, qty: 2 },
        ],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '88.97',
        shippingPrice: '100.00',
        taxPrice: '13.35',
        totalPrice: '202.32',
      })
    })
  })

  describe('Empty cart', () => {
    it('should calculate zero prices for empty cart', () => {
      const cart = {
        cartItems: [],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '0.00',
        shippingPrice: '100.00',
        taxPrice: '0.00',
        totalPrice: '100.00',
      })
    })
  })

  describe('Edge cases - floating point precision', () => {
    it('should handle tax calculation with floating point precision issues', () => {
      const cart = {
        cartItems: [{ price: 10.05, qty: 3 }],
      }
      const result = calculatePrices(cart)

      // This asserts current buggy behavior. Correct would be: taxPrice should be '4.52' (15% of 30.15)
      // but due to the calculation order: 0.15 * "30.15" -> floating point math issues
      expect(result).toEqual({
        itemsPrice: '30.15',
        shippingPrice: '100.00',
        taxPrice: '4.52',
        totalPrice: '134.67',
      })
    })

    it('should handle very small prices', () => {
      const cart = {
        cartItems: [{ price: 0.01, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '0.01',
        shippingPrice: '100.00',
        taxPrice: '0.00',
        totalPrice: '100.01',
      })
    })

    it('should handle high precision decimals that round down', () => {
      const cart = {
        cartItems: [{ price: 33.334, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '33.33',
        shippingPrice: '100.00',
        taxPrice: '5.00',
        totalPrice: '138.33',
      })
    })

    it('should handle high precision decimals that round up', () => {
      const cart = {
        cartItems: [{ price: 33.336, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '33.34',
        shippingPrice: '100.00',
        taxPrice: '5.00',
        totalPrice: '138.34',
      })
    })
  })

  describe('Malformed input - missing properties', () => {
    it('should throw error when cartItems is undefined', () => {
      const cart = {}
      expect(() => calculatePrices(cart)).toThrow(
        "Cannot read properties of undefined (reading 'reduce')"
      )
    })

    it('should throw error when cart is null', () => {
      expect(() => calculatePrices(null)).toThrow(
        "Cannot read properties of null (reading 'cartItems')"
      )
    })

    it('should throw error when cart is undefined', () => {
      expect(() => calculatePrices(undefined)).toThrow(
        "Cannot read properties of undefined (reading 'cartItems')"
      )
    })

    it('should throw error when cartItems is not an array', () => {
      const cart = {
        cartItems: 'not an array',
      }
      expect(() => calculatePrices(cart)).toThrow(
        "cart.cartItems.reduce is not a function"
      )
    })

    it('should throw error when cartItems is null', () => {
      const cart = {
        cartItems: null,
      }
      expect(() => calculatePrices(cart)).toThrow(
        "Cannot read properties of null (reading 'reduce')"
      )
    })
  })

  describe('Malformed input - invalid item data', () => {
    it('should return NaN when item missing price', () => {
      const cart = {
        cartItems: [{ qty: 1 }],
      }
      const result = calculatePrices(cart)

      // This asserts current buggy behavior. Correct would be: throw error or skip item
      // NaN is falsy in comparison, so NaN > 100 is false, shipping gets set to 100
      expect(result).toEqual({
        itemsPrice: 'NaN',
        shippingPrice: '100.00',
        taxPrice: 'NaN',
        totalPrice: 'NaN',
      })
    })

    it('should return NaN when item missing qty', () => {
      const cart = {
        cartItems: [{ price: 50 }],
      }
      const result = calculatePrices(cart)

      // This asserts current buggy behavior. Correct would be: treat missing qty as 1 or throw error
      // NaN is falsy in comparison, so NaN > 100 is false, shipping gets set to 100
      expect(result).toEqual({
        itemsPrice: 'NaN',
        shippingPrice: '100.00',
        taxPrice: 'NaN',
        totalPrice: 'NaN',
      })
    })

    it('should handle negative prices', () => {
      const cart = {
        cartItems: [{ price: -50, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '-50.00',
        shippingPrice: '100.00',
        taxPrice: '-7.50',
        totalPrice: '42.50',
      })
    })

    it('should handle negative quantities', () => {
      const cart = {
        cartItems: [{ price: 50, qty: -1 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '-50.00',
        shippingPrice: '100.00',
        taxPrice: '-7.50',
        totalPrice: '42.50',
      })
    })

    it('should handle string price (coerced to number)', () => {
      const cart = {
        cartItems: [{ price: '50', qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '50.00',
        shippingPrice: '100.00',
        taxPrice: '7.50',
        totalPrice: '157.50',
      })
    })

    it('should handle string qty (coerced to number)', () => {
      const cart = {
        cartItems: [{ price: 50, qty: '2' }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '100.00',
        shippingPrice: '100.00',
        taxPrice: '15.00',
        totalPrice: '215.00',
      })
    })
  })

  describe('Boundary conditions', () => {
    it('should handle very large cart value', () => {
      const cart = {
        cartItems: [{ price: 99999.99, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '99999.99',
        shippingPrice: '0.00',
        taxPrice: '15000.00',
        totalPrice: '114999.99',
      })
    })

    it('should handle many items in cart', () => {
      const items = Array(100).fill(null).map(() => ({ price: 1.50, qty: 1 }))
      const cart = { cartItems: items }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '150.00',
        shippingPrice: '0.00',
        taxPrice: '22.50',
        totalPrice: '172.50',
      })
    })

    it('should handle fractional quantities', () => {
      const cart = {
        cartItems: [{ price: 100, qty: 0.5 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '50.00',
        shippingPrice: '100.00',
        taxPrice: '7.50',
        totalPrice: '157.50',
      })
    })

    it('should handle zero quantity item', () => {
      const cart = {
        cartItems: [{ price: 100, qty: 0 }],
      }
      const result = calculatePrices(cart)

      expect(result).toEqual({
        itemsPrice: '0.00',
        shippingPrice: '100.00',
        taxPrice: '0.00',
        totalPrice: '100.00',
      })
    })
  })

  describe('Type coercion and comparison quirks', () => {
    it('should handle string itemsPrice in shipping calculation', () => {
      // itemsPrice is returned as string from addDecimals
      // but is compared as > 100 in shipping calculation
      const cart = {
        cartItems: [{ price: 150, qty: 1 }],
      }
      const result = calculatePrices(cart)

      // String '150.00' is coerced to number 150 in comparison
      expect(result).toEqual({
        itemsPrice: '150.00',
        shippingPrice: '0.00',
        taxPrice: '22.50',
        totalPrice: '172.50',
      })
    })

    it('should correctly handle itemsPrice string comparison with threshold', () => {
      const cart = {
        cartItems: [{ price: 100.01, qty: 1 }],
      }
      const result = calculatePrices(cart)

      // String '100.01' > 100 (numeric comparison works due to type coercion)
      expect(result).toEqual({
        itemsPrice: '100.01',
        shippingPrice: '0.00',
        taxPrice: '15.00',
        totalPrice: '115.01',
      })
    })
  })

  describe('Return types', () => {
    it('should always return strings for itemsPrice, shippingPrice, taxPrice', () => {
      const cart = {
        cartItems: [{ price: 50, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(typeof result.itemsPrice).toBe('string')
      expect(typeof result.shippingPrice).toBe('string')
      expect(typeof result.taxPrice).toBe('string')
    })

    it('should return string for totalPrice', () => {
      const cart = {
        cartItems: [{ price: 50, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(typeof result.totalPrice).toBe('string')
    })

    it('should return object with exact 4 properties', () => {
      const cart = {
        cartItems: [{ price: 50, qty: 1 }],
      }
      const result = calculatePrices(cart)

      expect(Object.keys(result)).toEqual([
        'itemsPrice',
        'shippingPrice',
        'taxPrice',
        'totalPrice',
      ])
    })
  })
})
