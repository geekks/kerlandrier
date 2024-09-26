require('dotenv').config()

const moment = require('moment') // for date handling
const ical = require('node-ical'); // for ical parsing
const strip = require ('string-strip-html');
const TBD_LOCATION_UID = process.env.TBD_LOCATION_UID 

const { getCorrespondingOaLocation} = require("./resources/getOaLocation")

/**
 * Get upcoming events from a remote ics file and return an array of Open Agenda-compatible events
 * @param {string} icsUrl - url of the ics file
 * @returns {Promise<Object[]>} - an array of Open Agenda-compatible events
 */
const pullUpcomingIcsEvents = async (icsUrl) => {
  const upcomingGaEvents = [];
  const data = await ical.fromURL(icsUrl);
  // Turn data object into an Array to filter based on value.type
  const dataAsArray = Object.entries(data);

  // Get the vCalendar metadata - used to enrich uid-externe
  const vCalendar = data.vcalendar;

  // // [NOT USED] Get the timezone
  // const timezoneFilter = dataAsArray.filter(([key, value]) => value.type === "VTIMEZONE");
  // const timezone = Object.fromEntries(timezoneFilter);

  // Get the actual event
  const eventsFilter = dataAsArray.filter(([key, value]) => {
    return (
      value.type === "VEVENT" &&
      moment(value.end).isAfter(moment())

    )
  });
  const events = Object.fromEntries(eventsFilter);

  for (const eventKey in events) {
    const icsEvent = data[eventKey];
    // console.log("icsEvent - ", icsEvent);
    // Check if start and end are more than 24 h
    const timings = []
    if (moment(icsEvent.end).diff(moment(icsEvent.start), 'hours') < 24) {
      timings.push({
        begin: moment(icsEvent.start).toISOString(),
        end: moment(icsEvent.end).toISOString()
      })
    } else {
      // Split into an array of items that are maximum 24h
      let begin = moment(icsEvent.start)
      let end = moment(icsEvent.end)
      while (begin.isBefore(end)) {
        timings.push({
          begin: begin.toISOString(),
          end: begin.add(24, 'hours').toISOString()
        })
        begin = begin.add(24, 'hours')
      }
    }

    const noHtmlicsEvent = strip.stripHtml(icsEvent.description ?? "-" ).result;

    // search or create OALocation. Default : "To be Defined"
    // const locationUId= getCorrespondingOaLocation(icsEvent.location)
    const locationUid = TBD_LOCATION_UID

    const newOaEvent = {
      "uid-externe": icsEvent.uid,
      slug: slugify(icsEvent.summary),
      title: { fr: icsEvent.summary },
      description: { fr: `${icsEvent.location}` },
      locationUid: locationUid,
      locationName: icsEvent.location,
      longDescription: { fr: noHtmlicsEvent },
      timings,
      onlineAccessLink: icsEvent.url,
      attendanceMode: 3, // 1 physique, 2 online, 3 mixte
      links: {
        link: icsEvent.url,
        data: {
          url: icsEvent.url
        }
      }
    }
    upcomingGaEvents.push(newOaEvent);
  }
  return upcomingGaEvents
}

const createOaEvent = async (oa, AGENDA_UID, event) => {
  return await oa.events.create(AGENDA_UID, event);
}

const updateOaEvent = async (oa, AGENDA_UID, eventUid, event) => {
  return await oa.events.update(AGENDA_UID, eventUid, event);
}

const patchOaEvent = async (oa, AGENDA_UID, eventUid, patch) => {
  return await oa.events.patch(AGENDA_UID, eventUid, patch);
}

const deleteOaEvents = async (oa, AGENDA_UID, uids) => {
  for (const uid of uids) {
    const result = await oa.events.delete(AGENDA_UID, uid);
    console.log("Deleted event:", result);
  }
  return uids
}

const slugify = text =>
  text
    .toString()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '')
    .replace(/--+/g, '-')

module.exports = { pullUpcomingIcsEvents, createOaEvent, updateOaEvent, patchOaEvent, deleteOaEvents, slugify }